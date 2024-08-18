import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CourseListComponent } from './course-list/course-list.component';
import { CourseFormComponent } from './course-form/course-form.component';

const routes: Routes = [
  { path: '', redirectTo: '/courses', pathMatch: 'full' },  // Default route
  { path: 'courses', component: CourseListComponent },       // Route for course list
  { path: 'courses/add', component: CourseFormComponent },   // Route for adding a new course
  { path: 'courses/edit/:id', component: CourseFormComponent } // Route for editing a course
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
