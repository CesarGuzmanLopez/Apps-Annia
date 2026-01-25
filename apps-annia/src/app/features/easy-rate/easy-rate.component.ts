import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, Injectable, NgZone, OnDestroy, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AppHeaderComponent } from '../../shared/app-header/app-header.component';

/** Interfaz para datos de una estructura molecular (Gaussian output) */
export interface Estructura {
  nombre: string;
  archivo?: string;
  temp?: number;
  eH_ts?: number; // Energía electrónica
  zpe?: number; // Zero-point energy
  frecNeg?: number; // Frecuencia negativa
  Thermal_Free_Energies?: number; // Energía libre de Gibbs térmica
}

/** Interfaz para parámetros de ejecución de cálculo */
export interface Ejecucion {
  title: string;
  react_1?: Estructura | null;
  react_2?: Estructura | null;
  transition_rate?: Estructura | null;
  product_1?: Estructura | null;
  product_2?: Estructura | null;
  tunneling?: boolean;
  cage_effects?: boolean;
  diffusion?: boolean;
  solvent?: string;
  radius_1?: number;
  radius_2?: number;
  reaction_distance?: number;
  degen?: number;
  print_data?: boolean;
  visc_custom?: number;
  temp?: number;
}

/** Interfaz para resultados del cálculo EasyRate */
export interface ResultadosEasyRate {
  titulo: string;
  entrada_resumen: string;
  resultados: {
    dHreact: number;
    dHact: number;
    Zreact: number;
    Zact: number;
    Greact: number;
    Gact: number;
    rateCte: number;
  };
  detalles: {
    temperatura: number;
    tunelamiento: boolean;
    difusion: boolean;
    solvent?: string;
    cage_effects: boolean;
  };
  eckart?: {
    Kappa: number;
    ALPH1: number;
    ALPH2: number;
    U: number;
  };
}

/** Servicio para cálculos termodinámicos y cinéticos */
@Injectable({ providedIn: 'root' })
export class EasyRateCalculatorService {
  // Constantes físicas internacionales (CODATA 2018)
  private readonly HARTREE_TO_KCAL = 627.5095;
  private readonly R_GAS_KCAL = 1.987 / 1000; // kcal·mol−1·K−1
  private readonly KB = 1.380649e-23; // J/K
  private readonly NA = 6.02214076e23;
  private readonly PI = 3.141592653589793;
  private readonly ANGSTROM_TO_M = 1e-10;
  private readonly H_PLANCK = 6.62607015e-34; // J·s
  private readonly C_LUZ = 299792458; // m/s
  private readonly BOLZ = 1.380649e-23; // J/K

  /** Gauss-Legendre 40-point weights for quadrature */
  private readonly GL_WEIGHTS = [
    0.0045213, 0.0104983, 0.0164211, 0.0222458, 0.027937, 0.0334602, 0.0387822, 0.0438709,
    0.0486958, 0.0532278, 0.0574398, 0.0613062, 0.064804, 0.067912, 0.0706116, 0.0728866, 0.0747232,
    0.0761104, 0.0770398, 0.0775059, 0.0775059, 0.0770398, 0.0761104, 0.0747232, 0.0728866,
    0.0706116, 0.067912, 0.064804, 0.0613062, 0.0574398, 0.0532278, 0.0486958, 0.0438709, 0.0387822,
    0.0334602, 0.027937, 0.0222458, 0.0164211, 0.0104983, 0.0045213,
  ];

  /** Gauss-Legendre 40-point nodes for quadrature */
  private readonly GL_NODES = [
    -0.9982377, -0.9907262, -0.9772599, -0.9579168, -0.9328128, -0.9020988, -0.8659595, -0.8246122,
    -0.7783057, -0.7273183, -0.6719567, -0.6125539, -0.5494671, -0.4830758, -0.4137792, -0.3419941,
    -0.2681522, -0.1926976, -0.1160841, -0.0387724, 0.0387724, 0.1160841, 0.1926976, 0.2681522,
    0.3419941, 0.4137792, 0.4830758, 0.5494671, 0.6125539, 0.6719567, 0.7273183, 0.7783057,
    0.8246122, 0.8659595, 0.9020988, 0.9328128, 0.9579168, 0.9772599, 0.9907262, 0.9982377,
  ];

  /**
   * Obtiene la viscosidad del disolvente en Pa·s
   */
  private getViscosity(solvent: string, viscCustom?: number): number {
    if (solvent?.toLowerCase() === 'other' && viscCustom && viscCustom > 0) {
      return viscCustom;
    }
    const viscosities: Record<string, number> = {
      benzene: 0.000604,
      'gas phase (air)': 0.000018,
      'pentyl ethanoate': 0.000742,
      water: 0.000891,
    };
    return viscosities[solvent?.toLowerCase()] || 0.001;
  }

  /**
   * Calcula los parámetros termodinámicos y constante de velocidad
   * Implementa el algoritmo completo de EasyRate con correcciones:
   * - Entalpía de reacción y activación
   * - Energías de punto cero
   * - Energías libres de Gibbs
   * - Correcciones por cage effects
   * - Factor de túnel por aproximación de Eckart
   * - Correcciones por difusión
   */
  calcularEasyRate(ejecucion: Ejecucion): ResultadosEasyRate {
    const titulo = ejecucion.title || 'Cálculo Easy Rate';
    const temp = ejecucion.temp || 298.15;
    const degen = ejecucion.degen || 1;
    const cageEffects = ejecucion.cage_effects || false;
    const diffusion = ejecucion.diffusion || false;

    // PASO 1: Calcular entalpías de reacción (ΔH)
    const dH_react =
      this.HARTREE_TO_KCAL *
      ((ejecucion.product_1?.eH_ts || 0) +
        (ejecucion.product_2?.eH_ts || 0) -
        (ejecucion.react_1?.eH_ts || 0) -
        (ejecucion.react_2?.eH_ts || 0));

    const dHact =
      this.HARTREE_TO_KCAL *
      ((ejecucion.transition_rate?.eH_ts || 0) -
        (ejecucion.react_1?.eH_ts || 0) -
        (ejecucion.react_2?.eH_ts || 0));

    // PASO 2: Calcular energías de punto cero (ZPE)
    const Zreact =
      this.HARTREE_TO_KCAL *
      ((ejecucion.product_2?.zpe || 0) +
        (ejecucion.product_1?.zpe || 0) -
        (ejecucion.react_1?.zpe || 0) -
        (ejecucion.react_2?.zpe || 0));

    const Zact =
      this.HARTREE_TO_KCAL *
      ((ejecucion.transition_rate?.zpe || 0) -
        (ejecucion.react_1?.zpe || 0) -
        (ejecucion.react_2?.zpe || 0));

    // PASO 3: Calcular energías libres de Gibbs con corrección de volumen molar
    const gibbsR1 = ejecucion.react_1?.Thermal_Free_Energies || 0;
    const gibbsR2 = ejecucion.react_2?.Thermal_Free_Energies || 0;
    const gibbsTS = ejecucion.transition_rate?.Thermal_Free_Energies || 0;
    const gibbsP1 = ejecucion.product_1?.Thermal_Free_Energies || 0;
    const gibbsP2 = ejecucion.product_2?.Thermal_Free_Energies || 0;

    const molarV = 0.08206 * temp;

    // Determinar número de especies (contar ceros en Gibbs)
    const countR = gibbsR1 === 0.0 || gibbsR2 === 0.0 ? 1 : 2;
    const countP = gibbsP1 === 0.0 || gibbsP2 === 0.0 ? 1 : 2;

    const deltaNr = countP - countR;
    const deltaNt = 1 - countR;

    const corr1Mr = this.R_GAS_KCAL * temp * Math.log(Math.pow(molarV, deltaNr));
    const corr1Mt = this.R_GAS_KCAL * temp * Math.log(Math.pow(molarV, deltaNt));

    // Energías libres de Gibbs
    let Greact = corr1Mr + this.HARTREE_TO_KCAL * (gibbsP2 + gibbsP1 - gibbsR1 - gibbsR2);
    let Gact = corr1Mt + this.HARTREE_TO_KCAL * (gibbsTS - gibbsR1 - gibbsR2);

    // PASO 4: Corrección por cage effects
    if (cageEffects && deltaNt !== 0) {
      const cageCorrAct =
        this.R_GAS_KCAL * temp * (Math.log(countR * Math.pow(10, 2 * countR - 2)) - (countR - 1));
      Gact -= cageCorrAct;
    }

    // PASO 5: Cálculo de factor de túnel (TST)
    let kappa = 1.0;
    let rateCte = NaN;
    let eckartParams: { Kappa: number; ALPH1: number; ALPH2: number; U: number } | null = null;

    if (Gact > 0) {
      // TST válida
      if (ejecucion.tunneling || Zact > 0) {
        // Aplicar corrección de Eckart si hay barrera ZPE o si se solicita túnel
        if (Zact > 0) {
          eckartParams = this.calcularEckart(
            Zact,
            Zreact,
            Math.abs(ejecucion.transition_rate?.frecNeg || 0),
            temp,
          );
          kappa = eckartParams.Kappa;
        }
      }
      // Calcular constante de velocidad TST
      rateCte = degen * kappa * (2.08e10 * temp * Math.exp(-Gact / (this.R_GAS_KCAL * temp)));
    }

    // PASO 6: Corrección por difusión
    if (diffusion && !isNaN(rateCte)) {
      const r1m = (ejecucion.radius_1 || 0) * this.ANGSTROM_TO_M;
      const r2m = (ejecucion.radius_2 || 0) * this.ANGSTROM_TO_M;
      const rrxnm = (ejecucion.reaction_distance || 0) * this.ANGSTROM_TO_M;
      const visc = this.getViscosity(ejecucion.solvent || '', ejecucion.visc_custom);

      const diffA = (this.KB * temp) / (6 * this.PI * visc * r1m);
      const diffB = (this.KB * temp) / (6 * this.PI * visc * r2m);
      const diffAB = diffA + diffB;

      const kDiff = 1000 * 4 * this.PI * diffAB * rrxnm * this.NA;
      rateCte = (kDiff * rateCte) / (kDiff + rateCte);
    }

    const entrada_resumen = this.generarResumenEntrada(ejecucion);

    return {
      titulo,
      entrada_resumen,
      resultados: {
        dHreact: dH_react,
        dHact,
        Zreact,
        Zact,
        Greact,
        Gact,
        rateCte,
      },
      detalles: {
        temperatura: temp,
        tunelamiento: ejecucion.tunneling || false,
        difusion: diffusion,
        solvent: ejecucion.solvent,
        cage_effects: cageEffects,
      },
      eckart: eckartParams || undefined,
    };
  }

  /**
   * Calcula el factor de túnel usando aproximación de Eckart con Gauss-Legendre
   */
  private calcularEckart(
    barrzpe: number,
    delzpe: number,
    freq: number,
    temp: number,
  ): { Kappa: number; ALPH1: number; ALPH2: number; U: number } {
    const CAL = 4184.0;
    const AV = 6.0221367e23;

    if (barrzpe <= 0 || freq <= 0) {
      return { Kappa: 1.0, ALPH1: NaN, ALPH2: NaN, U: NaN };
    }

    const ALPH1 = (2.0 * this.PI * barrzpe * CAL) / (AV * this.H_PLANCK * this.C_LUZ * freq);
    const ALPH2 =
      (2.0 * this.PI * (barrzpe - delzpe) * CAL) / (AV * this.H_PLANCK * this.C_LUZ * freq);
    const U = (this.H_PLANCK * this.C_LUZ * freq) / (this.BOLZ * temp);

    const PI2 = 2.0 * this.PI;
    const UPI2 = U / PI2;

    try {
      const C = 0.125 * this.PI * U * Math.pow(1.0 / Math.sqrt(ALPH1) + 1.0 / Math.sqrt(ALPH2), 2);
      const V1 = UPI2 * ALPH1;
      const V2 = UPI2 * ALPH2;
      const D = 4.0 * ALPH1 * ALPH2 - Math.pow(this.PI, 2);
      const DF = D > 0.0 ? Math.cosh(Math.sqrt(D)) : Math.cos(Math.sqrt(-D));
      const EZ = V2 >= V1 ? -V1 : -V2;
      const EM = 0.5 * (U - EZ);
      const EP = 0.5 * (U + EZ);

      let Kappa = 0.0;
      for (let j = 0; j < 40; j++) {
        const E = EM * this.GL_NODES[j] + EP;
        const A1 = this.PI * Math.sqrt((E + V1) / C);
        const A2 = this.PI * Math.sqrt((E + V2) / C);
        const FP = Math.cosh(A1 + A2);
        const FM = Math.cosh(A1 - A2);
        Kappa += this.GL_WEIGHTS[j] * Math.exp(-E) * ((FP - FM) / (FP + DF));
      }
      Kappa = EM * Kappa + Math.exp(-U);

      return { Kappa, ALPH1, ALPH2, U };
    } catch (error) {
      throw new Error('Energy barrier exceeded');
    }
  }

  private generarResumenEntrada(ejecucion: Ejecucion): string {
    return `Título: ${ejecucion.title}\nTemperatura: ${ejecucion.temp}K\nDegeneracidad: ${ejecucion.degen}`;
  }

  formatearResultados(resultados: ResultadosEasyRate): string {
    const res = resultados.resultados;
    const kStr = isNaN(res.rateCte)
      ? 'N/A (ΔG‡ ≤ 0, TST no válida)'
      : res.rateCte.toExponential(6) + ' s⁻¹';

    let output = `Resultados para: ${resultados.titulo}
${'='.repeat(60)}
CONSTANTE DE VELOCIDAD:
k = ${kStr}
${'='.repeat(60)}
ΔH (rxn): ${res.dHreact.toFixed(4)} kcal/mol
ΔH‡ (act): ${res.dHact.toFixed(4)} kcal/mol
ΔG (rxn): ${res.Greact.toFixed(4)} kcal/mol
ΔG‡ (act): ${res.Gact.toFixed(4)} kcal/mol
ZPE (rxn): ${res.Zreact.toFixed(4)} kcal/mol
ZPE‡ (act): ${res.Zact.toFixed(4)} kcal/mol`;

    // Agregar parámetros de Eckart si están disponibles
    if (resultados.eckart) {
      output += `\n${'='.repeat(60)}
PARÁMETROS DE TÚNEL (ECKART):
ALPH1: ${resultados.eckart.ALPH1.toFixed(4)}
ALPH2: ${resultados.eckart.ALPH2.toFixed(4)}
U: ${resultados.eckart.U.toFixed(4)}
κ (Kappa): ${resultados.eckart.Kappa.toFixed(4)}`;
    }

    return output;
  }
}

/** Servicio para parsear archivos de salida Gaussian */
@Injectable({ providedIn: 'root' })
export class EstructuraService {
  /**
   * Valida que el contenido sea un archivo Gaussian válido
   */
  private validarFormatoGaussian(contenido: string): boolean {
    return (
      contenido.includes('Gaussian') ||
      contenido.includes('SCF Done') ||
      contenido.includes('Frequency:')
    );
  }

  /**
   * Parsea un archivo Gaussian y extrae la estructura molecular
   * Implementa robustas expresiones regulares para extraer:
   * - Energía electrónica SCF
   * - Zero-point energy
   * - Frecuencias vibracionantes (especialmente imaginarias)
   * - Energía libre de Gibbs térmica
   */
  parsearArchivoGaussian(contenido: string): Estructura {
    if (!this.validarFormatoGaussian(contenido)) {
      throw new Error('El archivo no parece ser un archivo de salida Gaussian válido');
    }

    const estructura: Estructura = { nombre: 'Estructura' };

    // Energía electrónica SCF (Hartree)
    const energiaMatch = contenido.match(/SCF Done:.*?=\s*([-\d.]+)/);
    if (energiaMatch) {
      const energia = parseFloat(energiaMatch[1]);
      if (!isNaN(energia)) {
        estructura.eH_ts = energia;
      }
    }

    // Zero-point energy (Hartree)
    const zpeMatch = contenido.match(/Zero-point correction=\s*([-\d.]+)/);
    if (zpeMatch) {
      const zpe = parseFloat(zpeMatch[1]);
      if (!isNaN(zpe)) {
        estructura.zpe = zpe;
      }
    }

    // Frecuencias (toma la primera negativa si existe)
    const freqMatches = [
      ...contenido.matchAll(/Frequencies --\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)/g),
    ];
    if (freqMatches.length > 0) {
      const freqs = freqMatches
        .flatMap((m) => [m[1], m[2], m[3]].map((v) => parseFloat(v)))
        .filter((v) => !isNaN(v));
      const frecNegativa = freqs.find((f) => f < 0);
      if (frecNegativa !== undefined) {
        estructura.frecNeg = frecNegativa;
      }
    }

    // Gibbs free energy (Hartree) - soporta los dos formatos comunes
    const gibbsMatches = [
      ...contenido.matchAll(/Sum of electronic and thermal Free Energies=\s*([-\d.]+)/g),
    ];
    const gibbsAlt = contenido.match(/G=\s*([-\d.]+)\s*Hartree/);
    const gibbsValue =
      gibbsMatches.length > 0
        ? parseFloat(gibbsMatches[gibbsMatches.length - 1][1])
        : gibbsAlt
          ? parseFloat(gibbsAlt[1])
          : NaN;
    if (!isNaN(gibbsValue)) {
      estructura.Thermal_Free_Energies = gibbsValue;
    }

    // Temperatura (K)
    const tempMatch = contenido.match(/Temperature\s*=?\s*([\d.]+)\s*Kelvin/);
    if (tempMatch) {
      const temp = parseFloat(tempMatch[1]);
      if (!isNaN(temp)) {
        estructura.temp = temp;
      }
    }

    return estructura;
  }

  /**
   * Valida que una estructura tenga todos los parámetros necesarios
   */
  validarEstructura(estructura: Estructura): { valido: boolean; errores: string[] } {
    const errores: string[] = [];

    if (estructura.eH_ts === undefined || isNaN(estructura.eH_ts)) {
      errores.push('Energía electrónica (SCF) no encontrada');
    }

    // ZPE y Gibbs pueden faltar en algunos .log; no bloqueamos la carga, solo advertimos
    if (estructura.zpe === undefined || isNaN(estructura.zpe)) {
      errores.push('Zero-point energy no encontrado (se usará 0)');
      estructura.zpe = 0;
    }

    if (estructura.Thermal_Free_Energies === undefined || isNaN(estructura.Thermal_Free_Energies)) {
      errores.push('Energía libre de Gibbs térmica no encontrada (se usará 0)');
      estructura.Thermal_Free_Energies = 0;
    }

    return {
      valido: errores.length === 0 || (errores.length > 0 && !!estructura.eH_ts),
      errores,
    };
  }
}

@Component({
  selector: 'app-easy-rate',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, AppHeaderComponent],
  providers: [EasyRateCalculatorService, EstructuraService],
  templateUrl: './easy-rate.component.html',
  styleUrl: './easy-rate.component.scss',
})
export class EasyRateComponent implements OnInit, OnDestroy {
  form!: FormGroup;

  // Estructuras cargadas
  react_1: Estructura | null = null;
  react_2: Estructura | null = null;
  transition_rate: Estructura | null = null;
  product_1: Estructura | null = null;
  product_2: Estructura | null = null;

  // Resultados
  resultadosResumen = '';
  resultadosDetalles = '';

  // UI State
  loading = false;
  error: string | null = null;
  success: string | null = null;

  readonly solventes: ReadonlyArray<string> = [
    'Benzene',
    'Gas phase (Air)',
    'Pentyl ethanoate',
    'Water',
    'Other',
  ];

  private destroy$ = new Subject<void>();

  constructor(
    private fb: FormBuilder,
    private calculatorService: EasyRateCalculatorService,
    private estructuraService: EstructuraService,
    private router: Router,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone,
  ) {}

  ngOnInit(): void {
    this.initializeForm();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  irAlMenu(): void {
    this.router.navigate(['/menu']);
  }

  private initializeForm(): void {
    this.form = this.fb.group({
      title: ['Title', Validators.required],
      temperatura: [298.15, [Validators.required, Validators.min(0)]],
      tunelamiento: [true],
      degeneracy: [1, [Validators.required, Validators.min(1)]],
      cageEffects: [false],
      printData: [false],

      // Difusión
      diffusion: [false],
      solvent: ['', { disabled: true }],
      viscosity_custom: [{ value: '', disabled: true }],
      radius_1: [{ value: '', disabled: true }],
      radius_2: [{ value: '', disabled: true }],
      reaction_distance: [{ value: '', disabled: true }],
    });

    // Habilitar/deshabilitar controles de difusión
    this.form
      .get('diffusion')
      ?.valueChanges.pipe(takeUntil(this.destroy$))
      .subscribe((value: boolean) => {
        const controls = [
          'solvent',
          'viscosity_custom',
          'radius_1',
          'radius_2',
          'reaction_distance',
        ];
        controls.forEach((ctrl) => {
          const control = this.form.get(ctrl);
          if (value) {
            control?.enable();
          } else {
            control?.disable();
          }
        });
      });
  }

  /**
   * Maneja la selección de archivos Gaussian
   */
  onFileSelected(event: Event, role: string): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];

    if (!file) {
      this.error = 'No se seleccionó archivo';
      return;
    }

    // Validar extensión del archivo
    const validExtensions = ['.log', '.txt', '.out'];
    const hasValidExtension = validExtensions.some((ext) => file.name.toLowerCase().endsWith(ext));

    if (!hasValidExtension) {
      this.error = `Archivo inválido. Use archivos .log, .txt o .out. Recibido: ${file.name}`;
      return;
    }

    const reader = new FileReader();
    reader.onload = (e: ProgressEvent<FileReader>) => {
      this.ngZone.run(() => {
        try {
          const contenido = e.target?.result as string;
          if (!contenido) {
            this.error = `Archivo vacío: ${file.name}`;
            this.cdr.detectChanges();
            return;
          }

          const estructura = this.estructuraService.parsearArchivoGaussian(contenido);
          estructura.archivo = file.name;

          const validacion = this.estructuraService.validarEstructura(estructura);
          if (!validacion.valido) {
            this.error = `Error en ${role}:\n${validacion.errores.join('\n')}`;
            this.cdr.detectChanges();
            return;
          }

          this.asignarEstructura(role, estructura);
          this.error = null;
          this.success = `✓ ${role} cargado: ${file.name}`;
          this.cdr.detectChanges();
          setTimeout(() => {
            this.success = null;
            this.cdr.detectChanges();
          }, 3000);
        } catch (error) {
          this.error = `Error procesando archivo ${file.name}: ${error instanceof Error ? error.message : 'Error desconocido'}`;
          this.cdr.detectChanges();
        }
      });
    };

    reader.onerror = () => {
      this.error = `Error leyendo archivo: ${file.name}`;
    };

    reader.readAsText(file);
  }

  /**
   * Asigna una estructura al rol especificado
   */
  private asignarEstructura(role: string, estructura: Estructura): void {
    switch (role) {
      case 'React-1':
        this.react_1 = estructura;
        break;
      case 'React-2':
        this.react_2 = estructura;
        break;
      case 'Transition state':
        this.transition_rate = estructura;
        break;
      case 'Product-1':
        this.product_1 = estructura;
        break;
      case 'Product-2':
        this.product_2 = estructura;
        break;
    }
  }

  /**
   * Limpia una estructura cargada
   */
  limpiarEstructura(role: string): void {
    this.asignarEstructura(role, null!);
  }

  /**
   * Muestra los detalles de una estructura en un modal
   */
  verEstructura(estructura: Estructura | null): void {
    if (!estructura) return;
    const detalles = `
Archivo: ${estructura.archivo || 'N/A'}
Energía (hartree): ${estructura.eH_ts?.toFixed(6) || 'N/A'}
ZPE (hartree): ${estructura.zpe?.toFixed(6) || 'N/A'}
Frecuencia Neg: ${estructura.frecNeg?.toFixed(2) || 'N/A'} cm⁻¹
G (hartree): ${estructura.Thermal_Free_Energies?.toFixed(6) || 'N/A'}
Temperatura (K): ${estructura.temp?.toFixed(2) || 'N/A'}
    `;
    alert(detalles);
  }

  /**
   * Valida que todas las estructuras requeridas estén cargadas
   */
  private validarCarga(): { valido: boolean; mensaje: string } {
    if (!this.react_1) return { valido: false, mensaje: 'Reactante 1 no cargado' };
    if (!this.transition_rate) return { valido: false, mensaje: 'Estado de transición no cargado' };
    if (!this.product_1) return { valido: false, mensaje: 'Producto 1 no cargado' };

    return { valido: true, mensaje: '' };
  }

  /**
   * Ejecuta el cálculo termodinámico
   */
  async ejecutarCalculo(): Promise<void> {
    const validacion = this.validarCarga();
    if (!validacion.valido) {
      this.error = validacion.mensaje;
      return;
    }

    this.loading = true;
    this.error = null;
    this.success = null;

    try {
      const ejecucion: Ejecucion = {
        title: this.form.get('title')?.value || 'Cálculo Easy Rate',
        react_1: this.react_1,
        react_2: this.react_2,
        transition_rate: this.transition_rate,
        product_1: this.product_1,
        product_2: this.product_2,
        tunneling: this.form.get('tunelamiento')?.value === true,
        cage_effects:
          this.form.get('cageEffects')?.value ?? this.form.get('tunelamiento')?.value === true,
        diffusion: this.form.get('diffusion')?.value,
        solvent: this.form.get('solvent')?.value,
        radius_1: this.form.get('radius_1')?.value
          ? parseFloat(this.form.get('radius_1')?.value)
          : undefined,
        radius_2: this.form.get('radius_2')?.value
          ? parseFloat(this.form.get('radius_2')?.value)
          : undefined,
        reaction_distance: this.form.get('reaction_distance')?.value
          ? parseFloat(this.form.get('reaction_distance')?.value)
          : undefined,
        degen: parseFloat(this.form.get('degeneracy')?.value) || 1,
        temp: parseFloat(this.form.get('temperatura')?.value) || 298.15,
        visc_custom: this.form.get('viscosity_custom')?.value
          ? parseFloat(this.form.get('viscosity_custom')?.value)
          : undefined,
        print_data: this.form.get('printData')?.value,
      };

      const resultados = this.calculatorService.calcularEasyRate(ejecucion);
      this.resultadosResumen = this.calculatorService.formatearResultados(resultados);
      this.resultadosDetalles = this.generarDetallesResultados(resultados, ejecucion);

      this.success = 'Cálculo completado exitosamente';
    } catch (error) {
      this.error = `Error en el cálculo: ${error instanceof Error ? error.message : 'Error desconocido'}`;
    } finally {
      this.loading = false;
    }
  }

  /**
   * Genera un reporte detallado de los parámetros de entrada
   */
  private generarDetallesResultados(resultados: any, ejecucion: Ejecucion): string {
    let detalles = 'DETALLES DE ENTRADA\n' + '='.repeat(50) + '\n\n';

    detalles += `Título: ${ejecucion.title}\n`;
    detalles += `Temperatura: ${ejecucion.temp} K\n`;
    detalles += `Degeneracidad: ${ejecucion.degen}\n`;
    detalles += `Tunelamiento: ${ejecucion.tunneling ? 'Sí' : 'No'}\n`;
    detalles += `Cage Effects: ${ejecucion.cage_effects ? 'Sí' : 'No'}\n\n`;

    detalles += 'ESTRUCTURAS CARGADAS:\n';
    detalles += `Reactante 1: ${this.react_1?.archivo}\n`;
    if (this.react_2) detalles += `Reactante 2: ${this.react_2?.archivo}\n`;
    detalles += `Estado de Transición: ${this.transition_rate?.archivo}\n`;
    detalles += `Producto 1: ${this.product_1?.archivo}\n`;
    if (this.product_2) detalles += `Producto 2: ${this.product_2?.archivo}\n`;

    if (ejecucion.diffusion) {
      detalles += '\nPARÁMETROS DE DIFUSIÓN:\n';
      detalles += `Solvente: ${ejecucion.solvent}\n`;
      detalles += `Radio Reactante 1: ${ejecucion.radius_1} Å\n`;
      detalles += `Radio Reactante 2: ${ejecucion.radius_2} Å\n`;
      detalles += `Distancia de Reacción: ${ejecucion.reaction_distance} Å\n`;
    }

    return detalles;
  }

  /**
   * Limpia solo los resultados
   */
  limpiarResultados(): void {
    this.resultadosResumen = '';
    this.resultadosDetalles = '';
  }

  /**
   * Limpia todos los datos: estructuras, resultados y formulario
   */
  limpiarTodo(): void {
    this.limpiarResultados();
    this.react_1 = null;
    this.react_2 = null;
    this.transition_rate = null;
    this.product_1 = null;
    this.product_2 = null;
    this.initializeForm();
  }
}
