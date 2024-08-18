import { Component, OnInit, Input } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { NgForm } from '@angular/forms';
import { CourseService } from '../course.service';

@Component({
  selector: 'app-course-form',
  templateUrl: './course-form.component.html',
  styleUrls: ['./course-form.component.scss']
})
export class CourseFormComponent implements OnInit {
  @Input() courseId: string | null = null;
  
  courseData: any = {
    university: '',
    city: '',
    country: '',
    coursename: '',
    coursedescription: '',
    start_date: '',
    end_date: '',
    price: 0
  };
  isEditMode: boolean = false;

  constructor(private http: HttpClient, private route: ActivatedRoute, private router: Router, private courseService: CourseService) {}

  ngOnInit(): void {
    console.log(this);
    if (this.courseId) {
      this.isEditMode = true;
      this.loadCourse();
    }
  }
  

  loadCourse(): void {
    this.http.get<any>(`http://127.0.0.1:5000/${this.courseId}`)
      .subscribe(response => {
        this.courseData = response;
      }, error => {
        console.error('Error loading course:', error);
      });
  }

  saveCourse(form: NgForm): void {
    if (form.invalid) {
      return;
    }

    if (this.isEditMode) {
      this.http.put<any>(`http://127.0.0.1:5000/${this.courseId}`, this.courseData)
        .subscribe(response => {
          this.router.navigate(['/search']);
        }, error => {
          console.error('Error updating course:', error);
        });
    } else {
      this.http.post<any>('http://127.0.0.1:5000/', this.courseData)
        .subscribe(response => {
          this.router.navigate(['/search']);
        }, error => {
          console.error('Error creating course:', error);
        });
    }
  }

  // Add the onSubmit method
  // onSubmit(form: NgForm) {
  //   if (form.valid) {
  //     if (this.isEditMode) {
  //       // Update the course logic
  //       console.log('Course updated:', this.courseData);
  //     } else {
  //       // Create a new course logic
  //       console.log('New course created:', this.courseData);
  //     }
  //     // Here you can emit an event to the parent or navigate back to the course list
  //   } else {
  //     console.log('Form is invalid');
  //   }
  // }

  onSubmit(): void {
    
    if (this.isEditMode) {
      this.courseService.updateCourse(this.courseData.id, this.courseData).subscribe(
        () => {
          alert('Course updated successfully!');
          this.router.navigate(['/courses']); // Navigate back to the courses list
        },
        (error) => {
          console.error('Error updating course:', error);
        }
      );
    } else {
      this.courseService.addCourse(this.courseData).subscribe(
        () => {
          alert('Course added successfully!');
          this.router.navigate(['/courses']); // Navigate back to the courses list
        },
        (error) => {
          console.error('Error adding course:', error);
        }
      );
    }
  
  }

  onCancel() {
    // Logic to navigate back or reset the form
    this.router.navigate(['/courses']); // Example: Navigating back to the courses list
  }
}
