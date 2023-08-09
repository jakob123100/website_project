import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HelpComponent } from './help/help.component';
import { HttpClientModule } from '@angular/common/http';
import { LineChartComponent } from './line-chart/line-chart.component';

@NgModule({
  declarations: [
    AppComponent
  , HelpComponent, LineChartComponent],
  imports: [
    HttpClientModule,
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
