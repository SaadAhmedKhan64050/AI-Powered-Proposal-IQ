import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { StepperComponent } from '../../components/stepper/stepper.component';
import { RunResponse } from '../../models/proposal.model';
import { ProposalService } from '../../services/proposal.service';

@Component({
  selector: 'app-research-page',
  standalone: true,
  imports: [CommonModule, RouterLink, StepperComponent],
  templateUrl: './research-page.component.html',
  styleUrl: './research-page.component.css',
})
export class ResearchPageComponent implements OnInit {
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
        this.run = run;
        this.loading = false;
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

    this.proposalService.runOpportunities(this.runId).subscribe({
      next: () => {
        this.advancing = false;
        this.router.navigate(['/runs', this.runId, 'opportunities']);
      },
      error: (err: Error) => {
        this.advancing = false;
        this.errorMessage = err.message;
      },
    });
  }
}
