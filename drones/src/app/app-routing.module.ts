import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import {MapsComponent} from './dashboard/maps/maps.component';
import {ControlComponent} from './dashboard/control/control.component';
import {FarmsComponent} from './dashboard/farms/farms.component';
import {SettingsComponent} from './dashboard/settings/settings.component';
import {CreateFarmComponent} from './dashboard/farms/create-farm/create-farm.component';
import {ManageFarmComponent} from './dashboard/farms/manage-farm/manage-farm.component';

const routes: Routes = [

  { path: '', component: HomeComponent },
  { path: '',
    component: DashboardComponent,
    children: [
      {
        path: 'maps/:id',
        component: MapsComponent
      },
      {
        path: 'farms',
        component: FarmsComponent
      },
      {
        path: 'settings',
        component: SettingsComponent
      },
      {
        path: 'farms/create',
        component: CreateFarmComponent
      },
      {
        path: 'farms/:id',
        component: ManageFarmComponent
      },
      {
        path: 'gallery/:id',
        component: ControlComponent
      },
    ]
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {useHash: true})],
  exports: [RouterModule]
})
export class AppRoutingModule {

}
