import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FormsModule } from '@angular/forms';  // <-- Import FormsModule
import { HttpClientModule } from '@angular/common/http';  // <-- Import HttpClientModule

import { CourseSearchComponent } from './course-search/course-search.component';
import { CourseFormComponent } from './course-form/course-form.component';
import { CourseListComponent } from './course-list/course-list.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent,
    CourseSearchComponent,
    CourseFormComponent,
    CourseListComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,  // <-- Add FormsModule to imports array
    HttpClientModule, BrowserAnimationsModule  // <-- Add HttpClientModule to imports array for HTTP requests
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
