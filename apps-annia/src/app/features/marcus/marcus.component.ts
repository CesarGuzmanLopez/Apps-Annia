import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Estructura } from '../easy-rate/models/estructura.model';

type MarcusRole = 'react1' | 'react2' | 'prod1Adiab' | 'prod2Adiab' | 'prod1Vert' | 'prod2Vert';

interface RoleMeta {
  key: MarcusRole;
  title: string;
  hint: string;
}

interface MarcusResult {
  adiabaticEnergy: number;
  verticalEnergy: number;
  reorganization: number;
  barrier: number;
  rate: number;
  rateDiff?: number;
}

@Component({
  selector: 'app-marcus',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="marcus-container">
      <div class="header-nav">
        <button (click)="irAlMenu()" class="btn-back">← Menú</button>
        <div class="title-block">
          <h1>Marcuskin 1.1 (web)</h1>
          <p class="subtitle">Misma lógica del script de escritorio con archivos Gaussian</p>
        </div>
      </div>

      <section class="card">
        <header class="card-header">
          <div>
            <h2>Entrada</h2>
            <p>Carga los seis archivos Gaussian y define temperatura / difusión.</p>
          </div>
          <button class="link" type="button" (click)="limpiarTodo()">Limpiar</button>
        </header>

        <form class="grid" [formGroup]="form" (ngSubmit)="calcular()">
          <label class="field">
            <span>Título del pathway</span>
            <input formControlName="title" type="text" />
          </label>

          <label class="field">
            <span>Temperatura (K)</span>
            <input formControlName="temp" type="number" step="0.01" />
          </label>

          <div class="field toggle">
            <label>
              <input type="checkbox" formControlName="diffusion" />
              Considerar difusión
            </label>
            <small>Habilita corrección k<sub>diff</sub> tal como en la app original.</small>
          </div>

          <label class="field" [class.disabled]="!form.value.diffusion">
            <span>Radio Reactivo 1 (Å)</span>
            <input
              type="number"
              step="0.01"
              formControlName="radius1"
              [disabled]="!form.value.diffusion"
            />
          </label>

          <label class="field" [class.disabled]="!form.value.diffusion">
            <span>Radio Reactivo 2 (Å)</span>
            <input
              type="number"
              step="0.01"
              formControlName="radius2"
              [disabled]="!form.value.diffusion"
            />
          </label>

          <label class="field" [class.disabled]="!form.value.diffusion">
            <span>Distancia de reacción (Å)</span>
            <input
              type="number"
              step="0.01"
              formControlName="reactionDistance"
              [disabled]="!form.value.diffusion"
            />
          </label>

          <div class="actions">
            <button type="submit" class="btn-primary" [disabled]="form.invalid || !todoCargado">
              Calcular
            </button>
            <span class="status" [class.ok]="todoCargado" [class.bad]="!todoCargado">
              {{ todoCargado ? 'Archivos completos' : 'Faltan archivos' }}
            </span>
          </div>
        </form>

        <div class="upload-grid">
          <div class="upload" *ngFor="let role of roles">
            <p class="role-title">{{ role.title }}</p>
            <p class="hint">{{ role.hint }}</p>
            <input
              type="file"
              (change)="onFileSelected($event, role.key)"
              accept=".log,.out,.txt"
            />
            <p class="file" *ngIf="estructuras[role.key] as est">
              {{ est.nombre }} — SCF: {{ est.eH_ts | number: '1.6-6' }} Hartree
            </p>
          </div>
        </div>

        <div class="errors" *ngIf="error">{{ error }}</div>
      </section>

      <section class="card" *ngIf="resultado">
        <header class="card-header">
          <div>
            <h2>Resultados para {{ form.value.title }}</h2>
            <p>Constantes en las mismas unidades de la app (kcal/mol, s⁻¹).</p>
          </div>
        </header>
        <div class="result-grid">
          <div>
            <p class="label">ΔE adiabático (G) (kcal/mol)</p>
            <p class="value">{{ resultado.adiabaticEnergy | number: '1.2-2' }}</p>
          </div>
          <div>
            <p class="label">ΔE vertical (E) (kcal/mol)</p>
            <p class="value">{{ resultado.verticalEnergy | number: '1.2-2' }}</p>
          </div>
          <div>
            <p class="label">E reorganización λ (kcal/mol)</p>
            <p class="value">{{ resultado.reorganization | number: '1.2-2' }}</p>
          </div>
          <div>
            <p class="label">Barrera (kcal/mol)</p>
            <p class="value">{{ resultado.barrier | number: '1.2-2' }}</p>
          </div>
          <div>
            <p class="label">k (TST)</p>
            <p class="value">{{ resultado.rate | number: '1.2-2' }} s⁻¹</p>
          </div>
          <div *ngIf="resultado.rateDiff">
            <p class="label">k corregida por difusión</p>
            <p class="value">{{ resultado.rateDiff | number: '1.2-2' }} s⁻¹</p>
          </div>
        </div>
      </section>
    </div>
  `,
  styleUrl: './marcus.component.scss',
})
export class MarcusComponent {
  readonly roles: RoleMeta[] = [
    { key: 'react1', title: 'Reactivo 1 (SCF)', hint: 'Archivo Gaussian optimizado' },
    { key: 'react2', title: 'Reactivo 2 (SCF)', hint: 'Archivo Gaussian optimizado' },
    { key: 'prod1Adiab', title: 'Producto 1 (adiabático)', hint: 'Energía SCF optimizada' },
    { key: 'prod2Adiab', title: 'Producto 2 (adiabático)', hint: 'Energía SCF optimizada' },
    { key: 'prod1Vert', title: 'Producto 1 (vertical)', hint: 'Vertical energy' },
    { key: 'prod2Vert', title: 'Producto 2 (vertical)', hint: 'Vertical energy' },
  ];

  form!: FormGroup;

  estructuras: Record<MarcusRole, (Estructura & { nombre: string }) | null> = {
    react1: null,
    react2: null,
    prod1Adiab: null,
    prod2Adiab: null,
    prod1Vert: null,
    prod2Vert: null,
  };

  resultado: MarcusResult | null = null;
  error = '';

  private readonly HARTREE_TO_KCAL = 627.5095;
  private readonly kBoltz = 1.38066e-23;
  private readonly visc = 8.91e-4;
  private readonly PI = Math.PI;

  constructor(
    private readonly router: Router,
    private readonly fb: FormBuilder,
  ) {
    this.form = this.fb.group({
      title: ['Ruta', [Validators.required]],
      temp: [298.15, [Validators.required, Validators.min(0.1)]],
      diffusion: [false],
      radius1: [0],
      radius2: [0],
      reactionDistance: [0],
    });
  }

  get todoCargado(): boolean {
    return Object.values(this.estructuras).every(Boolean);
  }

  irAlMenu(): void {
    this.router.navigate(['/menu']);
  }

  limpiarTodo(): void {
    this.resultado = null;
    this.error = '';
    Object.keys(this.estructuras).forEach((key) => (this.estructuras[key as MarcusRole] = null));
    this.form.reset({
      title: 'Ruta',
      temp: 298.15,
      diffusion: false,
      radius1: 0,
      radius2: 0,
      reactionDistance: 0,
    });
  }

  onFileSelected(event: Event, role: MarcusRole): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const content = String(reader.result ?? '');
      try {
        const parsed = this.parseGaussian(content, file.name);
        this.estructuras[role] = parsed;
        this.error = '';
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Archivo inválido';
        this.estructuras[role] = null;
      }
    };
    reader.readAsText(file);
  }

  calcular(): void {
    if (!this.todoCargado) {
      this.error = 'Carga los seis archivos Gaussian.';
      return;
    }

    const temp = Number(this.form.value.temp);
    const diffusion = Boolean(this.form.value.diffusion);

    const r1 = this.estructuras.react1!;
    const r2 = this.estructuras.react2!;
    const p1a = this.estructuras.prod1Adiab!;
    const p2a = this.estructuras.prod2Adiab!;
    const p1v = this.estructuras.prod1Vert!;
    const p2v = this.estructuras.prod2Vert!;

    if ([r1, r2, p1a, p2a, p1v, p2v].some((e) => e.eH_ts === undefined)) {
      this.error = 'Falta energía SCF en algún archivo.';
      return;
    }

    const adiabaticEnergy =
      this.HARTREE_TO_KCAL *
      ((p1a.eH_ts || 0) + (p2a.eH_ts || 0) - (r1.eH_ts || 0) - (r2.eH_ts || 0));
    const adiabaticEnergyG =
      this.HARTREE_TO_KCAL *
      ((p1a.Thermal_Free_Energies || 0) +
        (p2a.Thermal_Free_Energies || 0) -
        (r1.Thermal_Free_Energies || 0) -
        (r2.Thermal_Free_Energies || 0));

    const verticalEnergy =
      this.HARTREE_TO_KCAL *
      ((p1v.eH_ts || 0) + (p2v.eH_ts || 0) - (r1.eH_ts || 0) - (r2.eH_ts || 0));

    const lambda = verticalEnergy - adiabaticEnergyG;
    if (lambda === 0) {
      this.error = 'λ = 0, revisa energías.';
      return;
    }

    const barrier = (lambda / 4) * Math.pow(1 + adiabaticEnergyG / lambda, 2);

    let rate = NaN;
    try {
      rate = 2.08366912663558e10 * temp * Math.exp((-1 * barrier * 1000) / (1.987 * temp));
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'No se pudo calcular k.';
      return;
    }

    let rateDiff: number | undefined;
    if (diffusion) {
      const radMolA = Number(this.form.value.radius1);
      const radMolB = Number(this.form.value.radius2);
      const reactDist = Number(this.form.value.reactionDistance);
      if ([radMolA, radMolB, reactDist].some((v) => !v || v <= 0)) {
        this.error = 'Ingresa radios y distancia para difusión (>0).';
        return;
      }
      const diffCoefA = (this.kBoltz * temp) / (6 * this.PI * this.visc * radMolA);
      const diffCoefB = (this.kBoltz * temp) / (6 * this.PI * this.visc * radMolB);
      const diffCoefAB = diffCoefA + diffCoefB;
      const kDiff = 1000 * 4 * this.PI * diffCoefAB * reactDist * 6.02e23;
      rateDiff = (kDiff * rate) / (kDiff + rate);
    }

    this.resultado = {
      adiabaticEnergy: adiabaticEnergyG,
      verticalEnergy,
      reorganization: lambda,
      barrier,
      rate,
      rateDiff,
    };
    this.error = '';
  }

  private parseGaussian(contenido: string, nombre: string): Estructura & { nombre: string } {
    if (!this.esGaussian(contenido)) {
      throw new Error(`El archivo ${nombre} no parece Gaussian.`);
    }

    const energiaMatch = contenido.match(/SCF Done:.*?=\s*([-\d.]+)/);
    const gibbsMatch = contenido.match(/Sum of electronic and thermal Free Energies=\s*([-\d.]+)/);

    const estructura: Estructura & { nombre: string } = { nombre };

    if (energiaMatch) {
      estructura.eH_ts = parseFloat(energiaMatch[1]);
    }
    if (gibbsMatch) {
      estructura.Thermal_Free_Energies = parseFloat(gibbsMatch[1]);
    }

    if (estructura.eH_ts === undefined || Number.isNaN(estructura.eH_ts)) {
      throw new Error(`No se encontró energía SCF en ${nombre}.`);
    }

    return estructura;
  }

  private esGaussian(contenido: string): boolean {
    return /Gaussian|SCF Done|Sum of electronic and thermal Free Energies/.test(contenido);
  }
}
