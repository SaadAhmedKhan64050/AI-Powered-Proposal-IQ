import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { StepperComponent } from '../../components/stepper/stepper.component';
import { RunResponse } from '../../models/proposal.model';
import { ProposalService } from '../../services/proposal.service';

@Component({
  selector: 'app-opportunities-page',
  standalone: true,
  imports: [CommonModule, RouterLink, StepperComponent],
  templateUrl: './opportunities-page.component.html',
  styleUrl: './opportunities-page.component.css',
})
export class OpportunitiesPageComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private proposalService = inject(ProposalService);

  runId = '';
  run: RunResponse | null = null;
  loading = true;
  advancing = false;
  errorMessage: string | null = null;

  ngOnInit(): void {
    this.runId = this.route.snapshot.paramMap.get('runId')!;
    this.proposalService.getRun(this.runId).subscribe({
      next: (run) => {
        if (run.opportunities.length === 0) {
          // Direct navigation before this stage ran yet — generate now.
          this.proposalService.runOpportunities(this.runId).subscribe({
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

  continue(): void {
    this.advancing = true;
    this.errorMessage = null;

    this.proposalService.runSolutions(this.runId).subscribe({
      next: () => {
        this.advancing = false;
        this.router.navigate(['/runs', this.runId, 'solutions']);
      },
      error: (err: Error) => {
        this.advancing = false;
        this.errorMessage = err.message;
      },
    });
  }
}
