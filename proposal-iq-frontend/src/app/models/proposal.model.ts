export interface CreateRunRequest {
  company_name: string;
  company_url: string;
  contact_name: string;
  contact_email: string;
}
export interface ResearchSection {
  heading: string;
  points: string[];
}

export interface Opportunity {
  title: string;
  description: string;
  evidence: string;
}

export interface MappedSolution {
  opportunity_title: string;
  solution_name: string;
  solution_description: string;
  rationale: string;
}
export interface RunResponse {
  run_id: string;
  company_name: string;
  contact_name: string;
  contact_email: string;
  research_sections: ResearchSection[];
  research_sources: string[];
  opportunities: Opportunity[];
  mapped_solutions: MappedSolution[];
  report_markdown: string;
  report_html: string;
  email_sent: boolean;
  email_error: string | null;
  warnings: string[];
}



export interface SolutionCatalogItem {
  name: string;
  description: string;
}

export interface ApiError {
  detail: string;
}
