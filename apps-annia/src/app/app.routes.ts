import { Routes } from '@angular/router';
import { EasyRateComponent } from './features/easy-rate/easy-rate.component';
import { MarcusComponent } from './features/marcus/marcus.component';
import { MenuComponent } from './features/menu/menu.component';
import { MolarFractionComponent } from './features/molar-fraction/molar-fraction.component';
import { TunnelComponent } from './features/tunnel/tunnel.component';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'menu',
    pathMatch: 'full',
  },
  {
    path: 'menu',
    component: MenuComponent,
  },
  {
    path: 'easy-rate',
    component: EasyRateComponent,
  },
  {
    path: 'marcus',
    component: MarcusComponent,
  },
  {
    path: 'molar-fraction',
    component: MolarFractionComponent,
  },
  {
    path: 'tunnel',
    component: TunnelComponent,
  },
];
