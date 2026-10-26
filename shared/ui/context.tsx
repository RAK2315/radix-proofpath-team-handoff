import { createContext, useContext } from "react";
import type {
  BenchmarkMode,
  Company,
  Extraction,
  Profile,
} from "../contracts/types";
export type View =
  "overview" | "jd" | "resume" | "profile" | "talent" | "matching";
export interface Workspace {
  profiles: Profile[];
  jds: Extraction[];
  resumes: Extraction[];
  profile: Profile | null;
  jd: Extraction | null;
  resume: Extraction | null;
  company: Company | null;
  companies: Company[];
  mode: BenchmarkMode;
  status: any;
  refresh: () => Promise<void>;
  refreshCompanies: () => Promise<void>;
  cacheExtraction: (value: Extraction) => void;
  cacheProfile: (value: Profile) => void;
  selectProfile: (id: string) => void;
  selectJD: (id: string) => void;
  selectResume: (id: string) => void;
  selectCompany: (id: string) => void;
  setMode: (mode: BenchmarkMode) => void;
  navigate: (view: View) => void;
  notify: (message: string) => void;
  showEvidence: (value: unknown) => void;
  showReceipt: (id: string) => void;
}
export const WorkspaceContext = createContext<Workspace>(null!);
export const useWorkspace = () => useContext(WorkspaceContext);
