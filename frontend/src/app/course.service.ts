import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CourseService {

  // private baseUrl = 'http://localhost:5000/api/courses'; // Replace with your backend URL
  //private baseUrl = 'http://localhost:5000/'; // Replace with your backend URL

  private baseUrl = 'https://pure-depths-08517-1676a3ff0ea5.herokuapp.com/'; // Replace with your backend URL
  constructor(private http: HttpClient) { }

  // Fetch courses with pagination
  getCourses(page: number, pageSize: number): Observable<any> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());

    return this.http.get<any>(`${this.baseUrl}`, { params });
  }

  // Search courses
  // searchCourses(query: string): Observable<any> {
  //   let params = new HttpParams().set('q', query);
  //   return this.http.get<any>(`${this.baseUrl}/search`, { params });
  // }

  searchCourses(query: string, page: number = 1, pageSize: number = 10): Observable<any> {
      const url = `${this.baseUrl}?query=${query}&page=${page}&page_size=${pageSize}`;
      return this.http.get<any>(url);
  }


  // Fetch course by ID
  getCourseById(id: number): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/${id}`);
  }

  // Create a new course
  addCourse(courseData: any): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}`, courseData);
  }

  // Update an existing course
  updateCourse(id: number, courseData: any): Observable<any> {
    return this.http.put<any>(`${this.baseUrl}/${id}`, courseData);
  }

  // Delete a course by ID
  deleteCourse(id: number): Observable<any> {
    return this.http.delete<any>(`${this.baseUrl}/${id}`);
  }
}
