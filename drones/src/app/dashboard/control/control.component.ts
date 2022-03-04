import { Component, OnInit } from '@angular/core';
import { NgxGalleryOptions, NgxGalleryImage, NgxGalleryAnimation } from 'ngx-gallery';
import { PerimeterService } from '../../services/perimeter.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-control',
  templateUrl: './control.component.html',
  styleUrls: ['./control.component.css']
})
export class ControlComponent implements OnInit {

  galleryOptions: NgxGalleryOptions[];
  galleryImages: NgxGalleryImage[];
  id;
  drones = [];
  selectedDrone = 0;
  
  constructor(private perimeterService: PerimeterService, private activatedRoute: ActivatedRoute) { 
    this.activatedRoute.params.subscribe((value) => {
      this.id = Number.parseInt(value.id, 10);
    });
  }

  ngOnInit() {
    this.galleryOptions = [
      { thumbnailsColumns: 3, thumbnailsRows: 2, thumbnailsPercent: 40, imagePercent: 60, thumbnailMargin: 2, thumbnailsMargin: 2, thumbnailsOrder: 2 },
      { breakpoint: 500, width: "300px", height: "300px", thumbnailsColumns: 3 },
      { breakpoint: 300, width: "100%", height: "200px", thumbnailsColumns: 2 }
    ];

    // this.galleryImages = [
    //   {
    //       small: 'assets/1-small.jpg',
    //       medium: 'assets/1-medium.jpg',
    //       big: 'assets/1-big.jpg'
    //   },
    //   {
    //       small: 'assets/2-small.jpg',
    //       medium: 'assets/2-medium.jpg',
    //       big: 'assets/2-big.jpg'
    //   },
    //   {
    //       small: 'assets/3-small.jpg',
    //       medium: 'assets/3-medium.jpg',
    //       big: 'assets/3-big.jpg'
    //   }
    // ];
    this.getDrones();
  }

  getPictures(drone) {
    if (drone !== this.selectedDrone) {
      this.perimeterService.getPictures(drone).subscribe((pictures: any[]) => {
        this.selectedDrone = drone;
        this.galleryImages = [];
        pictures.forEach(picture => {
          const im = 'http://localhost:5000/uploads/'+picture.image;
          this.galleryImages.push({'big': im, 'small': im, 'medium': im})
        });
      }, (error) => {console.log(error)});
    } else {
      this.selectedDrone = 0;
    }
  }


  getDrones() {
    this.perimeterService.getDrones(this.id).subscribe((drones: any[]) => {
        this.drones = drones;
        // console.log(this.drones);
    }, (error) => console.log(error));
  }


}
