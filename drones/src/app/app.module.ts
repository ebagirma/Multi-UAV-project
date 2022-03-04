import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NgxMapboxGLModule } from 'ngx-mapbox-gl';
import { HttpClientModule } from '@angular/common/http';
import { SidebarModule } from 'ng-sidebar';
import { HomeComponent } from './home/home.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { SidebarComponent } from './partials/sidebar/sidebar.component';
import { MapsComponent } from './dashboard/maps/maps.component';
import { FarmsComponent } from './dashboard/farms/farms.component';
import { CreateFarmComponent } from './dashboard/farms/create-farm/create-farm.component';
import { ManageFarmComponent } from './dashboard/farms/manage-farm/manage-farm.component';
import {FormsModule} from '@angular/forms';
import { ControlComponent } from './dashboard/control/control.component';

import { NgxGalleryModule } from 'ngx-gallery';
import { SettingsComponent } from './dashboard/settings/settings.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    DashboardComponent,
    SidebarComponent,
    MapsComponent,
    FarmsComponent,
    CreateFarmComponent,
    ManageFarmComponent,
    ControlComponent,
    SettingsComponent
  ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        HttpClientModule,
        NgxMapboxGLModule.withConfig({
            // tslint:disable-next-line:max-line-length
            accessToken: 'pk.eyJ1IjoibmF0bWlueWVsIiwiYSI6ImNqaW96Z2NxaDBzczkza3BtOTRmOTd2ZTMifQ.RgetO7wjYi5aNy1SzxnpFA', // Optionnal, can also be set per map (accessToken input of mgl-map)
        }),
        SidebarModule.forRoot(),
        NgxGalleryModule,
        FormsModule
    ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
