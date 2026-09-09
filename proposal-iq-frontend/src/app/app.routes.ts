import { Routes } from '@angular/router';

import { IntakePageComponent } from './pages/intake-page/intake-page.component';
import { ResearchPageComponent } from './pages/research-page/research-page.component';
import { OpportunitiesPageComponent } from './pages/opportunities-page/opportunities-page.component';
import { SolutionsPageComponent } from './pages/solutions-page/solutions-page.component';
import { EmailPageComponent } from './pages/email-page/email-page.component';

export const routes: Routes = [
  { path: '', component: IntakePageComponent },
  { path: 'runs/:runId/research', component: ResearchPageComponent },
  { path: 'runs/:runId/opportunities', component: OpportunitiesPageComponent },
  { path: 'runs/:runId/solutions', component: SolutionsPageComponent },
  { path: 'runs/:runId/email', component: EmailPageComponent },
  { path: '**', redirectTo: '' },
];
