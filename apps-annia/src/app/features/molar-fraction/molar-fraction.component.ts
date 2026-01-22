import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import {
  FormArray,
  FormBuilder,
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';

interface MolarRow {
  ph: number;
  fractions: number[];
}

@Component({
  selector: 'app-molar-fraction',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="molar-container">
      <div class="header-nav">
        <button (click)="irAlMenu()" class="btn-back">← Menú</button>
        <div class="title-block">
          <h1>Fracciones Molares 1.1</h1>
          <p class="subtitle">Replica la lógica del script Tkinter con pKas y rangos de pH.</p>
        </div>
      </div>

      <section class="card">
        <header class="card-header">
          <div>
            <h2>Entrada</h2>
            <p>Define cuántos pKa y el rango de pH.</p>
          </div>
          <button class="link" type="button" (click)="resetear()">Limpiar</button>
        </header>

        <form class="grid" [formGroup]="form" (ngSubmit)="calcular()">
          <label class="field">
            <span>Número de pKa</span>
            <select formControlName="numPkas" (change)="onChangePkaCount()">
              <option *ngFor="let n of [1, 2, 3, 4, 5, 6]" [value]="n">{{ n }}</option>
            </select>
          </label>

          <label class="field">
            <span>Modo de pH</span>
            <select formControlName="mode">
              <option value="single">Un valor</option>
              <option value="range">Rango</option>
            </select>
          </label>

          <label class="field" *ngIf="form.value.mode === 'single'">
            <span>pH único</span>
            <input type="number" step="0.01" formControlName="singlePh" />
          </label>

          <label class="field" *ngIf="form.value.mode === 'range'">
            <span>pH mínimo</span>
            <input type="number" step="0.01" formControlName="phMin" />
          </label>

          <label class="field" *ngIf="form.value.mode === 'range'">
            <span>pH máximo</span>
            <input type="number" step="0.01" formControlName="phMax" />
          </label>

          <label class="field" *ngIf="form.value.mode === 'range'">
            <span>Paso</span>
            <input type="number" step="0.01" formControlName="phStep" />
          </label>

          <div class="pk-grid">
            <label class="field" *ngFor="let ctrl of pkaControls.controls; let i = index">
              <span>pKa {{ i + 1 }}</span>
              <input type="number" step="0.01" [formControl]="ctrl" />
            </label>
          </div>

          <div class="actions">
            <button class="btn-primary" type="submit">Calcular</button>
            <div class="errors" *ngIf="error">{{ error }}</div>
          </div>
        </form>
      </section>

      <section class="card" *ngIf="resultado.length">
        <header class="card-header">
          <h2>Resultados</h2>
          <p>Fracciones molares f₀..fₙ calculadas como en el script original.</p>
        </header>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>pH</th>
                <th *ngFor="let idx of fractionIndexes">f{{ idx }}</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let row of resultado">
                <td>{{ row.ph | number: '1.2-2' }}</td>
                <td *ngFor="let frac of row.fractions">{{ frac | number: '1.3-3' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  `,
  styleUrl: './molar-fraction.component.scss',
})
export class MolarFractionComponent {
  form!: FormGroup;

  resultado: MolarRow[] = [];
  error = '';

  constructor(
    private readonly router: Router,
    private readonly fb: FormBuilder,
  ) {
    this.form = this.fb.group({
      numPkas: this.fb.control<number>(3, {
        nonNullable: true,
        validators: [Validators.required],
      }),
      mode: this.fb.control<'single' | 'range'>('single', {
        nonNullable: true,
        validators: [Validators.required],
      }),
      singlePh: this.fb.control<number>(7.0, { nonNullable: true }),
      phMin: this.fb.control<number>(0.0, { nonNullable: true }),
      phMax: this.fb.control<number>(14.0, { nonNullable: true }),
      phStep: this.fb.control<number>(0.1, { nonNullable: true }),
      pkaValues: this.fb.array<FormControl<number>>([
        this.fb.control<number>(4.5, { nonNullable: true }),
        this.fb.control<number>(8.0, { nonNullable: true }),
        this.fb.control<number>(10.0, { nonNullable: true }),
        this.fb.control<number>(0, { nonNullable: true }),
        this.fb.control<number>(0, { nonNullable: true }),
        this.fb.control<number>(0, { nonNullable: true }),
      ]),
    });
    this.onChangePkaCount();
  }

  get pkaControls(): FormArray<FormControl<number>> {
    return this.form.get('pkaValues') as FormArray<FormControl<number>>;
  }

  get fractionIndexes(): number[] {
    const n = Number(this.form.value.numPkas) || 0;
    return Array.from({ length: n + 1 }, (_, i) => i);
  }

  irAlMenu(): void {
    this.router.navigate(['/menu']);
  }

  onChangePkaCount(): void {
    const n = Number(this.form.value.numPkas) || 0;
    this.pkaControls.controls.forEach((ctrl, idx) => {
      if (idx < n) {
        ctrl.enable();
      } else {
        ctrl.disable();
      }
    });
  }

  resetear(): void {
    this.form.reset({
      numPkas: 3,
      mode: 'single',
      singlePh: 7.0,
      phMin: 0.0,
      phMax: 14.0,
      phStep: 0.1,
      pkaValues: this.pkaControls.value,
    });
    this.onChangePkaCount();
    this.resultado = [];
    this.error = '';
  }

  calcular(): void {
    try {
      const pks = this.obtenerPkas();
      const { ini, fin, step } = this.obtenerRango();
      this.resultado = this.calcularFracciones(pks, ini, fin, step);
      this.error = '';
    } catch (e) {
      this.error = e instanceof Error ? e.message : 'Datos inválidos';
      this.resultado = [];
    }
  }

  private obtenerPkas(): number[] {
    const n = Number(this.form.value.numPkas) || 0;
    const valores = this.pkaControls.value.slice(0, n).map((v: number) => Number(v));
    if (valores.some((v: number) => Number.isNaN(v))) {
      throw new Error('Introduce todos los pKa como números.');
    }
    return valores;
  }

  private obtenerRango(): { ini: number; fin: number; step: number } {
    if (this.form.value.mode === 'single') {
      const ph = Number(this.form.value.singlePh);
      if (Number.isNaN(ph)) throw new Error('pH inválido.');
      return { ini: ph, fin: ph, step: 0.1 };
    }
    const ini = Number(this.form.value.phMin);
    const fin = Number(this.form.value.phMax);
    const step = Number(this.form.value.phStep);
    if ([ini, fin, step].some((v) => Number.isNaN(v))) {
      throw new Error('Rango de pH inválido.');
    }
    if (step <= 0) throw new Error('El paso debe ser > 0.');
    return ini <= fin ? { ini, fin, step } : { ini: fin, fin: ini, step };
  }

  private calcularFracciones(pks: number[], ini: number, fin: number, step: number): MolarRow[] {
    const datos: MolarRow[] = [];
    let ph = ini;
    const limit = fin + step / 2;
    while (ph <= limit) {
      const fractions: number[] = [];
      for (let k = 0; k <= pks.length; k++) {
        fractions.push(this.FK(ph, k, pks));
      }
      datos.push({ ph, fractions });
      ph = +(ph + step).toFixed(10);
    }
    return datos;
  }

  private fBeta(k: number, pks: number[]): number {
    if (k > pks.length) throw new Error('k mayor que pk_a');
    let suma = 0.0;
    for (let i = 0; i < k; i++) {
      suma += pks[pks.length - i - 1];
    }
    return Math.pow(10, suma);
  }

  private F0(vPh: number, pks: number[]): number {
    let suma = 1.0;
    const conH = Math.pow(10, -vPh);
    for (let i = 0; i < pks.length; i++) {
      suma += this.fBeta(i + 1, pks) * Math.pow(conH, i + 1);
    }
    return 1 / suma;
  }

  private FK(vPh: number, K: number, pks: number[]): number {
    if (K === 0) return this.F0(vPh, pks);
    const conH = Math.pow(10, -vPh);
    return this.F0(vPh, pks) * this.fBeta(K, pks) * Math.pow(conH, K);
  }
}
