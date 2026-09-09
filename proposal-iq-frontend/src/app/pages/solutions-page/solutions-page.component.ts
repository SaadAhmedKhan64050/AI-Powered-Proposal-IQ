import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { StepperComponent } from '../../components/stepper/stepper.component';
import { RunResponse } from '../../models/proposal.model';
import { ProposalService } from '../../services/proposal.service';

@Component({
  selector: 'app-solutions-page',
  standalone: true,
  imports: [CommonModule, RouterLink, StepperComponent],
  templateUrl: './solutions-page.component.html',
  styleUrl: './solutions-page.component.css',
})
export class SolutionsPageComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private proposalService = inject(ProposalService);

  runId = '';
  run: RunResponse | null = null;
  loading = true;
  errorMessage: string | null = null;

  ngOnInit(): void {
    this.runId = this.route.snapshot.paramMap.get('runId')!;
    this.proposalService.getRun(this.runId).subscribe({
      next: (run) => {
        if (!run.mapped_solutions.length && !run.report_markdown) {
          this.proposalService.runSolutions(this.runId).subscribe({
            next: (updated) => {
              this.run = updated;
              this.loading = false;
            },
            error: (err: Error) => {
              this.errorMessage = err.message;
              this.loading = false;
            },
          });
        } else {
          this.run = run;
          this.loading = false;
        }
      },
      error: (err: Error) => {
        this.errorMessage = err.message;
        this.loading = false;
      },
    });
  }

  solutionFor(opportunityTitle: string) {
    return this.run?.mapped_solutions.find((s) => s.opportunity_title === opportunityTitle);
  }

  continue(): void {
    this.router.navigate(['/runs', this.runId, 'email']);
  }
}
