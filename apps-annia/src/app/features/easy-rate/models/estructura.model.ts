export interface Estructura {
  nombre: string;
  archivo?: string;
  temp?: number;
  eH_ts?: number;
  zpe?: number;
  frecNeg?: number;
  Thermal_Free_Energies?: number;
}

export interface Ejecucion {
  title: string;
  react_1?: Estructura;
  react_2?: Estructura;
  transition_rate?: Estructura;
  product_1?: Estructura;
  product_2?: Estructura;
  cage_effects?: boolean;
  diffusion?: boolean;
  solvent?: string;
  radius_1?: number;
  radius_2?: number;
  reaction_distance?: number;
  degen?: number;
  print_data?: boolean;
  visc_custom?: number;

  // Resultados
  dH_react?: number;
  dHact?: number;
  Zreact?: number;
  Zact?: number;
  Greact?: number;
  Gact?: number;
  rateCte?: number;
  frequency_negative?: number;
  temp?: number;
}

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
}
