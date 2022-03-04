import { Component, OnInit } from '@angular/core';
import { PerimeterService } from '../../services/perimeter.service';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css']
})
export class SettingsComponent implements OnInit {
  altitude = 0.0;
  spacing = 0.0;
  speed = 0.0;
  slope = 0.0;
  message = '';

  constructor(private perimeter: PerimeterService) {
  }

  ngOnInit() {
    this.getParameters(1);
  }

  changeParam(val, t) {
    if (t === 'altitude') this.altitude = val;
    else if (t === 'spacing') this.spacing = val;
    else if (t === 'speed') this.speed = val;
    else if (t === 'slope') this.slope = val;
  }

  getParameters(farm) {
    this.perimeter.getParameters(farm)
      .subscribe(({altitude, slope, spacing, speed}: any) => {
        this.altitude = altitude;
        this.slope = slope;
        this.spacing = spacing;
        this.speed = speed;
      }, (err) => console.log(err));
    
  }

  saveParameters() {
    const obj = {altitude: this.altitude, slope: this.slope, speed: this.speed, spacing: this.spacing, owner_id: 1};
    this.perimeter.saveParameters(obj)
    .subscribe((ret) => {
      console.log("Saved");
      this.message = "Successfully Saved!";
    }, (err) => {
      this.message = err.statusText;
    });
  }

}
