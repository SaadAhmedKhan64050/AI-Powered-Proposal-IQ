import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, catchError, throwError } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  ApiError,
  CreateRunRequest,
  RunResponse,
  SolutionCatalogItem,
} from '../models/proposal.model';

@Injectable({ providedIn: 'root' })
export class ProposalService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  createRun(request: CreateRunRequest): Observable<RunResponse> {
    return this.http
      .post<RunResponse>(`${this.baseUrl}/api/runs`, request)
      .pipe(catchError(this.toReadableError));
  }

  getRun(runId: string): Observable<RunResponse> {
    return this.http
      .get<RunResponse>(`${this.baseUrl}/api/runs/${runId}`)
      .pipe(catchError(this.toReadableError));
  }

  runOpportunities(runId: string): Observable<RunResponse> {
    return this.http
      .post<RunResponse>(`${this.baseUrl}/api/runs/${runId}/opportunities`, {})
      .pipe(catchError(this.toReadableError));
  }

  runSolutions(runId: string): Observable<RunResponse> {
    return this.http
      .post<RunResponse>(`${this.baseUrl}/api/runs/${runId}/solutions`, {})
      .pipe(catchError(this.toReadableError));
  }

  sendEmail(runId: string): Observable<RunResponse> {
    return this.http
      .post<RunResponse>(`${this.baseUrl}/api/runs/${runId}/send-email`, {})
      .pipe(catchError(this.toReadableError));
  }

  getSolutionsCatalog(): Observable<SolutionCatalogItem[]> {
    return this.http
      .get<SolutionCatalogItem[]>(`${this.baseUrl}/api/solutions`)
      .pipe(catchError(this.toReadableError));
  }

  /**
   * FastAPI returns errors as {"detail": "..."} for our HTTPExceptions, or a
   * Pydantic validation array for 422s. Normalize both into one string.
   */
  private toReadableError = (err: HttpErrorResponse) => {
    let message = 'Something went wrong talking to the server.';

    if (err.error) {
      const body: ApiError | { detail: Array<{ msg: string; loc: string[] }> } = err.error;
      if (typeof body.detail === 'string') {
        message = body.detail;
      } else if (Array.isArray(body.detail) && body.detail.length > 0) {
        message = body.detail
          .map((d) => `${d.loc[d.loc.length - 1]}: ${d.msg}`)
          .join('; ');
      }
    } else if (err.status === 0) {
      message = 'Could not reach the API. Is the backend running?';
    }

    return throwError(() => new Error(message));
  };
}
