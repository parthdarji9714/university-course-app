import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { CourseService } from '../course.service';


@Component({
  selector: 'app-course-list',
  templateUrl: './course-list.component.html',
  styleUrls: ['./course-list.component.scss']
})
export class CourseListComponent implements OnInit {
  courses: any[] = [];
  searchQuery: string = '';  // Add this line
  page: number = 1;
  pageSize: number = 10;
  totalCourses: number = 0;

  constructor(private http: HttpClient, private router: Router, private courseService: CourseService) {}

  ngOnInit(): void {
    this.loadCourses();
  }

  loadCourses(): void {
    const params = {
      page: this.page.toString(),
      page_size: this.pageSize.toString(),
      search: this.searchQuery   // Add search query to the params
    };
    this.http.get<any>('http://127.0.0.1:5000/', { params })
      .subscribe(response => {
        this.courses = response.courses;
        this.totalCourses = response.total_courses;
      }, error => {
        console.error('Error fetching courses:', error);
      });
  }

  deleteCourse(courseId: string): void {
    const confirmDelete = confirm('Are you sure you want to delete this course?');
    if (confirmDelete) {
      this.http.delete<any>(`http://127.0.0.1:5000/${courseId}`)
        .subscribe(response => {
          alert('Course deleted successfully!');
          this.loadCourses(); // Reload courses after deletion
        }, error => {
          console.error('Error deleting course:', error);
        });
    }
  }

  onPageChange(newPage: number): void {
    this.page = newPage;
    this.loadCourses();
  }

  course_length(start_date: string, end_date: string): number {
    const start = new Date(start_date);
    const end = new Date(end_date);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
  }

  get totalPages(): number {
    return Math.ceil(this.totalCourses / this.pageSize);
  }

  // Add this method
  // onSearch(): void {
  //   this.page = 1; // Reset to first page on new search
  //   this.loadCourses(); // Reload courses with the search query
  // }

  onSearch(): void {
    if (this.searchQuery.trim()) {
      this.courseService.searchCourses(this.searchQuery).subscribe(
          (response) => {
              this.courses = response.courses;
              this.totalCourses = response.total_courses;
              this.page = response.page;
              this.pageSize = response.page_size;
          },
          (error) => {
              console.error('Error searching courses:', error);
          }
      );
    } else {
      this.loadCourses();
    }
  }

  editCourse(courseId: string) {
    this.router.navigate(['/courses/edit', courseId]); 
  }
}
