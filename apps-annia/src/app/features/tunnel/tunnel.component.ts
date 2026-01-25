import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

interface TunnelResult {
  U: number;
  ALPH1: number;
  ALPH2: number;
  G: number;
}

@Component({
  selector: 'app-tunnel',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="tunnel-container">
      <div class="header-nav">
        <button (click)="irAlMenu()" class="btn-back">← Menú</button>
        <div class="spacer"></div>
        <div class="logo-section">
          <img src="tunnel-logo.png" alt="Tunnel Logo" class="app-logo">
        </div>
        <div class="title-block">
          <h1>Tunneling Effect Calculator</h1>
          <p class="subtitle">Eckart (CLRP) con la misma lógica del código original</p>
        </div>
      </div>

      <section class="card">
        <header class="card-header">
          <div>
            <h2>Datos de entrada</h2>
            <p>Usa las mismas unidades que el programa de escritorio.</p>
          </div>
          <button type="button" class="link" (click)="restablecer()">Limpiar</button>
        </header>

        <form class="grid" [formGroup]="form" (ngSubmit)="calcular()">
          <label class="field">
            <span>Reaction barrier ZPE (kcal/mol)</span>
            <input type="number" formControlName="barrZPE" step="0.01" />
            <small>Corresponde a BARRZPE en el script de Python.</small>
          </label>

          <label class="field">
            <span>Reaction energy ZPE (kcal/mol)</span>
            <input type="number" formControlName="delZPE" step="0.01" />
            <small>Corresponde a DELZPE.</small>
          </label>

          <label class="field">
            <span>Frecuencia imaginaria (cm⁻¹, positiva)</span>
            <input type="number" formControlName="freq" step="0.1" />
            <small>El código original espera el valor sin signo.</small>
          </label>

          <label class="field">
            <span>Temperatura (K)</span>
            <input type="number" formControlName="temp" step="0.1" />
          </label>

          <div class="actions">
            <button type="submit" class="btn-primary" [disabled]="form.invalid">Calcular</button>
            <div class="errors" *ngIf="error">
              {{ error }}
            </div>
          </div>
        </form>
      </section>

      <section class="card" *ngIf="resultado">
        <header class="card-header">
          <h2>Resultado</h2>
          <p>Valores calculados con la cuadratura de Gauss-Legendre (40 puntos).</p>
        </header>
        <div class="result-grid">
          <div>
            <p class="label">U</p>
            <p class="value">{{ resultado.U | number: '1.3-3' }}</p>
          </div>
          <div>
            <p class="label">α₁</p>
            <p class="value">{{ resultado.ALPH1 | number: '1.3-3' }}</p>
          </div>
          <div>
            <p class="label">α₂</p>
            <p class="value">{{ resultado.ALPH2 | number: '1.3-3' }}</p>
          </div>
          <div>
            <p class="label">G</p>
            <p class="value">{{ resultado.G | number: '1.3-3' }}</p>
          </div>
        </div>
      </section>
    </div>
  `,
  styleUrl: './tunnel.component.scss',
})
export class TunnelComponent {
  form!: FormGroup;

  resultado: TunnelResult | null = null;
  error = '';

  // Coeficientes de la cuadratura Gauss-Legendre de orden 40
  private readonly Y = [
    -0.9982377, -0.9907262, -0.9772599, -0.9579168, -0.9328128, -0.9020988, -0.8659595, -0.8246122,
    -0.7783057, -0.7273183, -0.6719567, -0.6125539, -0.5494671, -0.4830758, -0.4137792, -0.3419941,
    -0.2681522, -0.1926976, -0.1160841, -0.0387724, 0.0387724, 0.1160841, 0.1926976, 0.2681522,
    0.3419941, 0.4137792, 0.4830758, 0.5494671, 0.6125539, 0.6719567, 0.7273183, 0.7783057,
    0.8246122, 0.8659595, 0.9020988, 0.9328128, 0.9579168, 0.9772599, 0.9907262, 0.9982377,
  ];

  private readonly W = [
    0.0045213, 0.0104983, 0.0164211, 0.0222458, 0.027937, 0.0334602, 0.0387822, 0.0438709,
    0.0486958, 0.0532278, 0.0574398, 0.0613062, 0.064804, 0.067912, 0.0706116, 0.0728866, 0.0747232,
    0.0761104, 0.0770398, 0.0775059, 0.0775059, 0.0770398, 0.0761104, 0.0747232, 0.0728866,
    0.0706116, 0.067912, 0.064804, 0.0613062, 0.0574398, 0.0532278, 0.0486958, 0.0438709, 0.0387822,
    0.0334602, 0.027937, 0.0222458, 0.0164211, 0.0104983, 0.0045213,
  ];

  private readonly AV = 6.0221367e23;
  private readonly HPLANCK = 6.6260755e-34;
  private readonly CLUZ = 2.9979246e10;
  private readonly BOLZ = 1.380658e-23;
  private readonly CAL = 4184.0;
  private readonly PI = Math.PI;

  constructor(
    private readonly router: Router,
    private readonly fb: FormBuilder,
  ) {
    this.form = this.fb.group({
      barrZPE: [0, [Validators.required]],
      delZPE: [0, [Validators.required]],
      freq: [0, [Validators.required]],
      temp: [298.15, [Validators.required, Validators.min(0.1)]],
    });
  }

  irAlMenu(): void {
    this.router.navigate(['/menu']);
  }

  restablecer(): void {
    this.form.reset({ barrZPE: 0, delZPE: 0, freq: 0, temp: 298.15 });
    this.resultado = null;
    this.error = '';
  }

  calcular(): void {
    if (this.form.invalid) {
      this.error = 'Completa todos los campos con valores válidos.';
      return;
    }

    const barrZPE = Number(this.form.value.barrZPE);
    const delZPE = Number(this.form.value.delZPE);
    const freq = Number(this.form.value.freq);
    const temp = Number(this.form.value.temp);

    if (freq <= 0) {
      this.error = 'La frecuencia debe ser positiva (usa valor absoluto).';
      return;
    }

    try {
      const res = this.calcularEckart(barrZPE, delZPE, freq, temp);
      this.resultado = res;
      this.error = '';
    } catch (e) {
      this.error = e instanceof Error ? e.message : 'No se pudo calcular.';
      this.resultado = null;
    }
  }

  private calcularEckart(
    barrZPE: number,
    delZPE: number,
    freq: number,
    temp: number,
  ): TunnelResult {
    const ALPH1 = (2 * this.PI * barrZPE * this.CAL) / (this.AV * this.HPLANCK * this.CLUZ * freq);
    const ALPH2 =
      (2 * this.PI * (barrZPE - delZPE) * this.CAL) / (this.AV * this.HPLANCK * this.CLUZ * freq);
    const U = (this.HPLANCK * this.CLUZ * freq) / (this.BOLZ * temp);

    const PI2 = 2 * this.PI;
    const UPI2 = U / PI2;
    const C = 0.125 * this.PI * U * Math.pow(1 / Math.sqrt(ALPH1) + 1 / Math.sqrt(ALPH2), 2);
    const V1 = UPI2 * ALPH1;
    const V2 = UPI2 * ALPH2;
    const D = 4 * ALPH1 * ALPH2 - Math.pow(this.PI, 2);
    const DF = D > 0 ? Math.cosh(Math.sqrt(D)) : Math.cos(Math.sqrt(-D));
    const EZ = V2 >= V1 ? -V1 : -V2;
    const EM = 0.5 * (U - EZ);
    const EP = 0.5 * (U + EZ);

    let G = 0;
    for (let j = 0; j < 40; j++) {
      const E = EM * this.Y[j] + EP;
      const A1 = this.PI * Math.sqrt((E + V1) / C);
      const A2 = this.PI * Math.sqrt((E + V2) / C);
      const FP = Math.cosh(A1 + A2);
      const FM = Math.cosh(A1 - A2);
      G += (this.W[j] * Math.exp(-E) * (FP - FM)) / (FP + DF);
    }

    G = EM * G + Math.exp(-U);

    if (Number.isNaN(G) || Number.isNaN(ALPH1) || Number.isNaN(ALPH2) || Number.isNaN(U)) {
      throw new Error('Energy barrier o frecuencia fuera de rango.');
    }

    return { U, ALPH1, ALPH2, G };
  }
}
