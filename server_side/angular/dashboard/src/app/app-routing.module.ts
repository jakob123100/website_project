import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { TemperaturePageComponent } from './temperature-page/temperature-page.component';
import { PowerPageComponent } from './power-page/power-page.component';
import { EnergyPageComponent } from './energy-page/energy-page.component';

const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'dashboard/temperature', component: TemperaturePageComponent },
  { path: 'dashboard/power', component: PowerPageComponent },
  { path: 'dashboard/energy', component: EnergyPageComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
