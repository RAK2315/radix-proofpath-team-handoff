export const categories: Record<string, string> = {
  COD: "Coding",
  DSA: "Data Structures & Algorithms",
  OOD: "Object-Oriented Design",
  APTI: "Aptitude",
  COMM: "Communication",
  AI: "AI",
  CLOUD: "Cloud",
  SQL: "SQL",
  SWE: "Software Engineering",
  SYSD: "System Design",
  NETW: "Networking",
  OS: "Operating Systems",
};
// Response payloads include every Pydantic default. Schemas are generated from the API.
import type { components } from "./generated";
type Complete<T> = T extends (infer U)[]
  ? Complete<U>[]
  : T extends object
    ? { [K in keyof T]-?: Complete<T[K]> }
    : T;
export type Skill = Complete<components["schemas"]["Skill"]>;
export type Requirement = Complete<components["schemas"]["Requirement"]>;
export type Extraction = Complete<components["schemas"]["Extraction"]>;
export type Rating = Complete<components["schemas"]["Rating"]>;
export type Profile = Complete<components["schemas"]["Profile"]>;
export interface Company {
  id: string;
  name: string;
}
export type BenchmarkMode = "real" | "synthetic";
export function blankProfile(): Profile {
  return {
    schema_version: "1.0",
    id: crypto.randomUUID(),
    revision: 1,
    name: "",
    email: "",
    education: [],
    skills: [],
    hackathons: [],
    internships: [],
    certifications: [],
    preferred_roles: [],
    projects: [],
    experience: [],
    achievements: [],
    cv_file: null,
    ratings: Object.keys(categories).map((category_code) => ({
      category_code,
      level: null,
      origin: "self_reported",
    })),
  };
}
export function manualSkill(name = "New skill"): Skill {
  return {
    skill_id: crypto.randomUUID(),
    skill_name: name,
    category_code: "OTHER",
    skill_family: "Other",
    evidence: "Manual claim",
    confidence: "low",
    source_page: null,
    source_file: null,
    source_document_id: null,
    source_type: "manual",
    evidence_type: "manual_entry",
    verification_status: "unverified",
    claim_status: "claimed",
    claim_basis: "explicit",
    normalized_name: null,
    source_start: null,
    source_end: null,
  };
}
