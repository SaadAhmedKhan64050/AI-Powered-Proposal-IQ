import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RouterLink } from '@angular/router';

export interface StepDef {
  label: string;
  path: string; // relative to /runs/:runId/
}

@Component({
  selector: 'app-stepper',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './stepper.component.html',
  styleUrl: './stepper.component.css',
})
export class StepperComponent {
  @Input({ required: true }) runId!: string;
  @Input({ required: true }) currentIndex!: number; // 0-based
  @Input() furthestUnlockedIndex = 0; // steps beyond this aren't clickable yet

  steps: StepDef[] = [
    { label: 'Research', path: 'research' },
    { label: 'Opportunities', path: 'opportunities' },
    { label: 'Solutions', path: 'solutions' },
    { label: 'Email', path: 'email' },
  ];
}
