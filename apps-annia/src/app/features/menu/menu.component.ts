import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss',
})
export class MenuComponent {
  apps = [
    {
      id: 'easy-rate',
      nombre: 'Easy Rate 2.0',
      descripcion:
        'Cálculo de constantes de velocidad con correcciones termodinámicas y de difusión',
      icono: '⚡',
      ruta: '/easy-rate',
    },
    {
      id: 'marcus',
      nombre: 'Marcus',
      descripcion: 'Teoría de Marcus para transferencia electrónica',
      icono: '🔄',
      ruta: '/marcus',
    },
    {
      id: 'molar-fraction',
      nombre: 'Molar Fraction',
      descripcion: 'Cálculo de fracciones molares',
      icono: '⚗️',
      ruta: '/molar-fraction',
    },
    {
      id: 'tunnel',
      nombre: 'Tunnel',
      descripcion: 'Análisis de tunelamiento cuántico',
      icono: '🌀',
      ruta: '/tunnel',
    },
  ];

  constructor(private router: Router) {}

  irA(ruta: string) {
    this.router.navigate([ruta]);
  }
}
