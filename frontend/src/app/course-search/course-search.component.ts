import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-course-search',
  templateUrl: './course-search.component.html',
  styleUrls: ['./course-search.component.scss']
})
export class CourseSearchComponent implements OnInit {
  courses: any[] = [];
  searchQuery: string = '';
  page: number = 1;
  pageSize: number = 10;
  totalCourses: number = 0;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.searchCourses();
  }

  searchCourses(): void {
    const params = {
      query: this.searchQuery,
      page: this.page.toString(),
      page_size: this.pageSize.toString()
    };
    this.http.get<any>('http://127.0.0.1:5000/api/courses', { params })
      .subscribe(response => {
        this.courses = response.courses;
        this.totalCourses = response.total_courses;
      }, error => {
        console.error('Error fetching courses:', error);
      });
  }

  onSearch(): void {
    this.page = 1;  // Reset to the first page on a new search
    this.searchCourses();
  }

  onPageChange(newPage: number): void {
    this.page = newPage;
    this.searchCourses();
  }
}
