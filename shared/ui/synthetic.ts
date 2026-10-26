import { blankProfile } from "../contracts/types";
import type { Extraction, Profile } from "../contracts/types";
import { api, apiResponse } from "./api";

/** A labelled development journey through the same public APIs as real uploads. */
export async function loadSyntheticWalkthrough() {
  const upload = async (kind: string, index: number) => {
    const response = await apiResponse(`/examples/${kind}/${index}`);
    if (!response.ok) throw new Error("Synthetic example unavailable");
    const data = new FormData();
    data.append(
      "file",
      new File([await response.blob()], `synthetic-${kind}-${index}.docx`, {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      }),
    );
    const extracted = await api<Extraction>(`/${kind}/extract`, {
      method: "POST",
      body: data,
    });
    return api<Extraction>(`/${kind}/${extracted.id}`, {
      method: "PATCH",
      body: JSON.stringify({ ...extracted, review_status: "reviewed" }),
    });
  };
  const jd = await upload("jd", 0),
    resume = await upload("resumes", 0);
  const profile = blankProfile();
  Object.assign(profile, {
    name: resume.name,
    email: resume.email,
    education: resume.education,
    projects: resume.projects,
    experience: resume.experience,
    certifications: resume.certifications,
    achievements: resume.achievements,
    skills: resume.skills,
    cv_file: resume.document_id,
    preferred_roles: ["Platform Engineer"],
    ratings: profile.ratings.map((rating, index) => ({
      ...rating,
      level: [6, 5, 5, 5, 6, 3, 4, 5, 6, 4, 4, 5][index],
    })),
  });
  const saved = await api<Profile>("/profiles", {
    method: "POST",
    body: JSON.stringify(profile),
  });
  return { jd, resume, profile: saved };
}
