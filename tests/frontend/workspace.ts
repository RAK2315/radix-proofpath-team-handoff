import { vi } from "vitest";
import { blankProfile } from "../../shared/contracts/types";
import type { Extraction } from "../../shared/contracts/types";
import type { Workspace } from "../../shared/ui/context";

export function extraction(source_type: "jd" | "resume" = "jd"): Extraction {
  return {
    schema_version: "1.0",
    id: "synthetic-extraction",
    revision: 1,
    source_type,
    source_file: "synthetic.docx",
    company: null,
    role: null,
    skills: [],
    requirement_groups: [],
    name: "Synthetic",
    email: "",
    education: [],
    projects: [],
    experience: [],
    certifications: [],
    internships: [],
    hackathons: [],
    achievements: [],
    input_method: "file",
    sections: [],
    review_status: "reviewed",
    extraction_mode: "local_limited",
    parser_version: "local-vocabulary-1.0",
    model_version: null,
    prompt_version: null,
    llm_status: "not_requested",
    llm_metadata: {},
    warnings: [],
    document_id: null,
  };
}
export function workspace(patch: Partial<Workspace> = {}): Workspace {
  return {
    profiles: [],
    jds: [],
    resumes: [],
    profile: null,
    jd: null,
    resume: null,
    company: null,
    companies: [],
    mode: "real",
    status: { llm_configured: false },
    refresh: vi.fn().mockResolvedValue(undefined),
    refreshCompanies: vi.fn().mockResolvedValue(undefined),
    cacheExtraction: vi.fn(),
    cacheProfile: vi.fn(),
    selectProfile: vi.fn(),
    selectJD: vi.fn(),
    selectResume: vi.fn(),
    selectCompany: vi.fn(),
    setMode: vi.fn(),
    navigate: vi.fn(),
    notify: vi.fn(),
    showEvidence: vi.fn(),
    showReceipt: vi.fn(),
    ...patch,
  };
}
export function syntheticProfile() {
  return { ...blankProfile(), name: "Synthetic UI Candidate" };
}
