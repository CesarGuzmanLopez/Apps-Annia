import { Injectable } from '@angular/core';
import { Estructura } from '../models/estructura.model';

@Injectable({
  providedIn: 'root',
})
export class EstructuraService {
  constructor() {}

  parsearArchivoGaussian(contenido: string): Estructura {
    const estructura: Estructura = {
      nombre: 'Estructura',
    };

    // Parsear energía
    const energiaMatch = contenido.match(/SCF Done:.*?=\s*([-\d.]+)/);
    if (energiaMatch) {
      estructura.eH_ts = parseFloat(energiaMatch[1]);
    }

    // Parsear ZPE
    const zpeMatch = contenido.match(/Zero-point correction=\s*([\d.]+)/);
    if (zpeMatch) {
      estructura.zpe = parseFloat(zpeMatch[1]);
    }

    // Parsear frecuencia imaginaria
    const freqMatch = contenido.match(/imaginary frequencies \(negative Signs\):\s*([-\d.,\s]+)/);
    if (freqMatch) {
      const freqs = freqMatch[1]
        .split(',')
        .map((f) => parseFloat(f.trim()))
        .filter((f) => !isNaN(f));
      if (freqs.length > 0) {
        estructura.frecNeg = Math.min(...freqs);
      }
    }

    // Parsear Gibbs Free Energy
    const gibbsMatch = contenido.match(/Sum of electronic and thermal Free Energies=\s*([-\d.]+)/);
    if (gibbsMatch) {
      estructura.Thermal_Free_Energies = parseFloat(gibbsMatch[1]);
    }

    // Parsear temperatura
    const tempMatch = contenido.match(/Temperature\s*([\d.]+)\s*Kelvin/);
    if (tempMatch) {
      estructura.temp = parseFloat(tempMatch[1]);
    }

    return estructura;
  }

  validarEstructura(estructura: Estructura): { valido: boolean; errores: string[] } {
    const errores: string[] = [];

    if (!estructura.eH_ts || isNaN(estructura.eH_ts)) {
      errores.push('Energía electrónica no encontrada');
    }

    if (!estructura.zpe || isNaN(estructura.zpe)) {
      errores.push('Energía de punto cero no encontrada');
    }

    if (estructura.frecNeg !== undefined && estructura.frecNeg > 0) {
      errores.push('Se espera una frecuencia imaginaria negativa para estados de transición');
    }

    return {
      valido: errores.length === 0,
      errores,
    };
  }
}
