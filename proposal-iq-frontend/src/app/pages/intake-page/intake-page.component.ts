import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

import { ProposalFormComponent } from '../../components/proposal-form/proposal-form.component';
import { CreateRunRequest } from '../../models/proposal.model';
import { ProposalService } from '../../services/proposal.service';

@Component({
  selector: 'app-intake-page',
  standalone: true,
  imports: [CommonModule, ProposalFormComponent],
  templateUrl: './intake-page.component.html',
  styleUrl: './intake-page.component.css',
})
export class IntakePageComponent {
  private proposalService = inject(ProposalService);
  private router = inject(Router);

  submitting = false;
  errorMessage: string | null = null;

  onSubmit(request: CreateRunRequest): void {
    this.submitting = true;
    this.errorMessage = null;

    this.proposalService.createRun(request).subscribe({
      next: (run) => {
        this.submitting = false;
        this.router.navigate(['/runs', run.run_id, 'research']);
      },
      error: (err: Error) => {
        this.submitting = false;
        this.errorMessage = err.message;
      },
    });
  }
}
