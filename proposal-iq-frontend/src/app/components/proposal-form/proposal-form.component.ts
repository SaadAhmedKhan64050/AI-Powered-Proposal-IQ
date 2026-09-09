import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { CreateRunRequest } from '../../models/proposal.model';

@Component({
  selector: 'app-proposal-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './proposal-form.component.html',
  styleUrl: './proposal-form.component.css',
})
export class ProposalFormComponent {
  @Input() submitting = false;
  @Output() submitProposal = new EventEmitter<CreateRunRequest>();

  private fb = inject(FormBuilder);

  form = this.fb.group({
    company_name: ['', [Validators.required, Validators.maxLength(200)]],
    company_url: ['', [Validators.required, this.urlValidator]],
    contact_name: ['', [Validators.required, Validators.maxLength(200)]],
    contact_email: ['', [Validators.required, Validators.email]],
  });

  private urlValidator(control: { value: string }) {
    if (!control.value) return null;
    try {
      new URL(control.value);
      return null;
    } catch {
      return { invalidUrl: true };
    }
  }

  get f() {
    return this.form.controls;
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.submitProposal.emit(this.form.getRawValue() as CreateRunRequest);
  }
}
