import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { StepperComponent } from '../../components/stepper/stepper.component';
import { RunResponse } from '../../models/proposal.model';
import { ProposalService } from '../../services/proposal.service';

@Component({
  selector: 'app-email-page',
  standalone: true,
  imports: [CommonModule, RouterLink, StepperComponent],
  templateUrl: './email-page.component.html',
  styleUrl: './email-page.component.css',
})
export class EmailPageComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private proposalService = inject(ProposalService);

  runId = '';
  run: RunResponse | null = null;
  loading = true;
  sending = false;
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

  send(): void {
    // Sending only ever happens from this explicit click — no page in this
    // wizard sends email as a side effect of loading or navigating.
    this.sending = true;
    this.errorMessage = null;

    this.proposalService.sendEmail(this.runId).subscribe({
      next: (updated) => {
        this.run = updated;
        this.sending = false;
      },
      error: (err: Error) => {
        this.errorMessage = err.message;
        this.sending = false;
      },
    });
  }
}
