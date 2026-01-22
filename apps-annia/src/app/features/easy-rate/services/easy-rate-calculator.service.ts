import { Injectable } from '@angular/core';
import { Ejecucion, ResultadosEasyRate } from '../models/estructura.model';

@Injectable({
  providedIn: 'root',
})
export class EasyRateCalculatorService {
  private readonly HARTREE_TO_KCAL = 627.5095;
  private readonly R_GAS_KCAL = 1.987 / 1000;
  private readonly KB = 1.380649e-23;
  private readonly NA = 6.02214076e23;
  private readonly PI = 3.141592653589793;
  private readonly ANGSTROM_TO_M = 1e-10;

  constructor() {}

  calcularEasyRate(ejecucion: Ejecucion): ResultadosEasyRate {
    const titulo = ejecucion.title || 'Cálculo Easy Rate';

    // Calcular entalpías de reacción
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

    // Calcular energías de punto cero
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

    // Calcular energías libres de Gibbs
    const gibbsR1 = ejecucion.react_1?.Thermal_Free_Energies || 0;
    const gibbsR2 = ejecucion.react_2?.Thermal_Free_Energies || 0;
    const gibbsTS = ejecucion.transition_rate?.Thermal_Free_Energies || 0;
    const gibbsP1 = ejecucion.product_1?.Thermal_Free_Energies || 0;
    const gibbsP2 = ejecucion.product_2?.Thermal_Free_Energies || 0;

    const temp = ejecucion.temp || 298.15;
    const molarV = 0.08206 * temp;

    const countR = gibbsR1 === 0 || gibbsR2 === 0 ? 1 : 2;
    const countP = gibbsP1 === 0 || gibbsP2 === 0 ? 1 : 2;

    const deltaNr = countP - countR;
    const deltaNt = 1 - countR;

    let Greact = (gibbsP1 + gibbsP2 - gibbsR1 - gibbsR2) * this.HARTREE_TO_KCAL;
    if (deltaNr !== 0) {
      Greact += this.R_GAS_KCAL * temp * Math.log(molarV ** deltaNr);
    }

    let Gact = (gibbsTS - gibbsR1 - gibbsR2) * this.HARTREE_TO_KCAL;
    if (deltaNt !== 0) {
      Gact += this.R_GAS_KCAL * temp * Math.log(molarV ** deltaNt);
    }

    // Calcular constante de velocidad
    let rateCte = this.calcularConstanteVelocidad(Gact, temp, ejecucion.degen || 1);

    // Aplicar tunelamiento si está habilitado
    if (ejecucion.cage_effects) {
      rateCte = this.aplicarTunelamiento(rateCte, temp);
    }

    // Aplicar difusión si está habilitada
    if (ejecucion.diffusion) {
      rateCte = this.aplicarDifusion(
        rateCte,
        temp,
        ejecucion.radius_1 || 0,
        ejecucion.radius_2 || 0,
        ejecucion.reaction_distance || 0,
        ejecucion.solvent || '',
        ejecucion.visc_custom,
      );
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
        tunelamiento: ejecucion.cage_effects || false,
        difusion: ejecucion.diffusion || false,
        solvent: ejecucion.solvent,
        cage_effects: ejecucion.cage_effects || false,
      },
    };
  }

  private calcularConstanteVelocidad(dG: number, temp: number, degen: number): number {
    const h = 6.62607015e-34;
    const kB = 1.380649e-23;
    const c = 2.99792458e8;
    const NA = 6.02214076e23;

    const dG_J = (dG * 1000 * 4.184) / NA;
    const exponente = -dG_J / (8.314 * temp);
    const k = ((kB * temp) / h) * Math.exp(exponente) * degen;

    return k;
  }

  private aplicarTunelamiento(k: number, temp: number): number {
    // Aplicar corrección de tunelamiento (Wigner)
    const hc = 6.62607015e-34 * 2.99792458e8;
    const h_bar = 1.054571817e-34;
    const nu_imag = (100 * h_bar * 3e10) / (1.380649e-23 * temp);

    const factor_wigner = 1 + (1 / 24) * nu_imag ** 2;
    return k * factor_wigner;
  }

  private aplicarDifusion(
    k: number,
    temp: number,
    radius1: number,
    radius2: number,
    distancia_reaccion: number,
    solvent: string,
    visc_custom?: number,
  ): number {
    if (!radius1 || !radius2 || !distancia_reaccion) {
      return k;
    }

    const visc = this.obtenerViscosidad(solvent, visc_custom);
    if (!visc || visc <= 0) {
      return k;
    }

    const r_sum = (radius1 + radius2) * this.ANGSTROM_TO_M;
    const d_reac = distancia_reaccion * this.ANGSTROM_TO_M;
    const NA = this.NA;
    const kB_J = this.KB;

    const kDiff = (8 * Math.PI * NA * d_reac * ((kB_J * temp) / visc)) / 1000;
    return (kDiff * k) / (kDiff + k);
  }

  private obtenerViscosidad(solvent: string, visc_custom?: number): number {
    if (solvent?.toLowerCase() === 'other' && visc_custom && visc_custom > 0) {
      return visc_custom;
    }

    switch (solvent) {
      case 'Benzene':
        return 0.000604;
      case 'Gas phase (Air)':
        return 0.000018;
      case 'Pentyl ethanoate':
        return 0.000862;
      case 'Water':
        return 0.000891;
      default:
        return 0;
    }
  }

  private generarResumenEntrada(ejecucion: Ejecucion): string {
    const lineas = [
      `Título: ${ejecucion.title}`,
      `Temperatura: ${ejecucion.temp}K`,
      `Tunelamiento: ${ejecucion.cage_effects ? 'Sí' : 'No'}`,
      `Degeneracidad: ${ejecucion.degen}`,
      `Difusión: ${ejecucion.diffusion ? 'Sí' : 'No'}`,
      ejecucion.diffusion ? `Solvente: ${ejecucion.solvent}` : '',
    ].filter((x) => x !== '');

    return lineas.join('\n');
  }

  formatearResultados(resultados: ResultadosEasyRate): string {
    const res = resultados.resultados;
    return `
Resultados para: ${resultados.titulo}
${'='.repeat(50)}

ENTALPÍAS (kcal/mol):
  ΔH reacción:  ${res.dHreact.toExponential(6)}
  ΔH activación: ${res.dHact.toExponential(6)}

ENERGÍAS DE PUNTO CERO (kcal/mol):
  Z reacción:   ${res.Zreact.toExponential(6)}
  Z activación: ${res.Zact.toExponential(6)}

ENERGÍAS LIBRES DE GIBBS (kcal/mol):
  ΔG reacción:  ${res.Greact.toExponential(6)}
  ΔG activación: ${res.Gact.toExponential(6)}

CONSTANTE DE VELOCIDAD:
  k = ${res.rateCte.toExponential(6)} s⁻¹ (unimolecular)

CONDICIONES:
  Temperatura: ${resultados.detalles.temperatura.toFixed(2)} K
  Tunelamiento: ${resultados.detalles.tunelamiento ? 'Activado' : 'Desactivado'}
  Difusión: ${resultados.detalles.difusion ? `Activada (${resultados.detalles.solvent})` : 'Desactivada'}
${'='.repeat(50)}
    `;
  }
}
