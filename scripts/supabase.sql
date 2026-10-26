-- Apply only to an authorized TEAM-OWNED project. Never alter official staging tables.
create table if not exists public.proofpath_records (
  owner uuid not null references auth.users(id) on delete cascade,
  kind text not null check (kind in ('profile','jd','resume','document','receipt')),
  id uuid not null,
  revision integer not null default 1,
  payload jsonb not null,
  updated_at timestamptz not null default now(),
  primary key (owner, kind, id)
);
alter table public.proofpath_records enable row level security;
revoke all on public.proofpath_records from anon;
drop policy if exists "Own ProofPath records" on public.proofpath_records;
create policy "Own ProofPath records" on public.proofpath_records
for all to authenticated using (auth.uid() = owner) with check (auth.uid() = owner);
grant select,insert,update,delete on public.proofpath_records to authenticated;

-- Private original documents. This script never touches organizer benchmark tables.
insert into storage.buckets (id, name, public, file_size_limit)
values ('proofpath-documents', 'proofpath-documents', false, 10485760)
on conflict (id) do update set public=false, file_size_limit=10485760;
drop policy if exists "Own ProofPath originals" on storage.objects;
create policy "Own ProofPath originals" on storage.objects
for all to authenticated
using (bucket_id='proofpath-documents' and (storage.foldername(name))[1] = auth.uid()::text)
with check (bucket_id='proofpath-documents' and (storage.foldername(name))[1] = auth.uid()::text);

-- All inference budget mutations happen inside a security-definer transaction.
-- Call reservations include two attempts and a deliberately conservative token estimate.
create table if not exists public.proofpath_usage (
  bucket text not null, day date not null, calls integer not null default 0,
  tokens bigint not null default 0, primary key(bucket,day)
);
alter table public.proofpath_usage enable row level security;
revoke all on public.proofpath_usage from anon, authenticated;
create or replace function public.proofpath_reserve_extraction(p_tokens integer)
returns void language plpgsql security definer set search_path = '' as $$
declare owner_id uuid := auth.uid(); day_key date := (now() at time zone 'UTC')::date;
begin
  if owner_id is null or p_tokens < 1 or p_tokens > 300000 then
    raise exception 'INVALID_QUOTA_RESERVATION';
  end if;
  -- Lock global row first in every transaction to avoid inverse-order deadlocks.
  insert into public.proofpath_usage(bucket,day) values ('global',day_key) on conflict do nothing;
  update public.proofpath_usage set calls=calls+1, tokens=tokens+p_tokens
    where bucket='global' and day=day_key and calls<300 and tokens+p_tokens<=10000000;
  if not found then raise exception 'QUOTA_EXCEEDED'; end if;
  insert into public.proofpath_usage(bucket,day) values (owner_id::text,day_key) on conflict do nothing;
  update public.proofpath_usage set calls=calls+1, tokens=tokens+p_tokens
    where bucket=owner_id::text and day=day_key and calls<50 and tokens+p_tokens<=2000000;
  if not found then raise exception 'QUOTA_EXCEEDED'; end if;
end;
$$;
revoke all on function public.proofpath_reserve_extraction(integer) from public, anon;
grant execute on function public.proofpath_reserve_extraction(integer) to authenticated;
