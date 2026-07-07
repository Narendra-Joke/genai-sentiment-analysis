import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, Chart, registerables } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { ProductService } from '../../services/product';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef } from '@angular/core';

Chart.register(...registerables);
Chart.register(ChartDataLabels);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class DashboardComponent implements OnInit {

  constructor(
    private productService: ProductService,
    private http: HttpClient,
    private cd: ChangeDetectorRef
  ) {}

  @ViewChild(BaseChartDirective) chart?: BaseChartDirective;

  productLoaded=false;
  componentLoaded=false;
  isInitialState = true;

  productName='';
  productImage='';
  releasedDate='';
  chipset='';
  memory='';
  camera='';
  battery='';

  componentName='';

  positive=0;
  negative=0;

  positiveReviewCount=0;
  negativeReviewCount=0;

  totalReviews=0;

  componentPositiveCounts:number[]=[];
  componentNegativeCounts:number[]=[];
  componentDataAvailable:boolean = true;

  sourcePositiveCounts:number[]=[];
  sourceNegativeCounts:number[]=[];
  sourceDataAvailable:boolean=true;

  countryDataAvailable:boolean = true;

  doughnutChartData: ChartConfiguration<'doughnut'>['data']={
    labels:['Positive','Negative'],
    datasets:[
      {
        data:[0,0],
        backgroundColor:['#2e7d32','#d32f2f']
      }
    ]
  };

  doughnutChartOptions: ChartConfiguration<'doughnut'>['options']={
    responsive:true,
    cutout:'55%',
    plugins:{
      legend:{position:'top'},
      tooltip:{
        callbacks:{
          label:(context)=>{
            const label=context.label;
            const value=context.raw as number;

            if(label==='Positive'){
              return `Positive : ${this.positiveReviewCount} (${value}%)`;
            }

            if(label==='Negative'){
              return `Negative : ${this.negativeReviewCount} (${value}%)`;
            }

            return `${label}: ${value}%`;
          }
        }
      },
      datalabels:{
        color:'#ffffff',
        font:{weight:'bold',size:14},
        formatter:(value)=> value + '%'
      }
    }
  };

  barChartData: ChartConfiguration<'bar'>['data']={
    labels:[],
    datasets:[
      {
        label:'Positive',
        data:[],
        backgroundColor:'#4caf50'
      },
      {
        label:'Negative',
        data:[],
        backgroundColor:'#e53935'
      }
    ]
  };

  barChartOptions: ChartConfiguration<'bar'>['options']={
    responsive:true,
    scales:{
      y:{
        beginAtZero:true,
        max:100,
        ticks:{
          callback:(value)=> value + '%'
        }
      }
    },
    plugins:{
      legend:{position:'top'},

      datalabels: {
        color: '#ffffff',        
        font: {
          weight: 'bold',
          size: 12
        },
        formatter: (value: number) => value + '%'
      },

      tooltip:{
        callbacks:{
          label:(context)=>{

            const label=context.dataset.label;
            const percentage=context.raw as number;
            const index=context.dataIndex;

            const positiveCount=this.componentPositiveCounts[index];
            const negativeCount=this.componentNegativeCounts[index];

            if(label==='Positive'){
              return `Positive: ${positiveCount} (${percentage}%)`;
            }

            if(label==='Negative'){
              return `Negative: ${negativeCount} (${percentage}%)`;
            }

            return `${label}: ${percentage}%`;
          }
        }
      }
    }
  };

  // source wise sentiment

  sourceChartData: ChartConfiguration<'bar'>['data']={
  labels:[],
  datasets:[
    {
      label:'Positive',
      data:[],
      backgroundColor:'#4caf50',
      stack:'sentiment',
      barThickness:18,
      maxBarThickness:18,
      categoryPercentage:0.3,
      barPercentage:0.5
    },
    {
      label:'Negative',
      data:[],
      backgroundColor:'#e53935',
      stack:'sentiment',
      barThickness:18,
      maxBarThickness:18,
      categoryPercentage:0.3,
      barPercentage:0.5
    }
  ]
  };

sourceChartOptions: ChartConfiguration<'bar'>['options']={
  responsive:true,
  scales:{
    x:{
      stacked:true,
      offset: true
    },
    y:{
      stacked:true,
      beginAtZero:true,
      max:100,
      ticks:{
        callback:(value)=> value + '%'
      }
    }
  },
  plugins:{
    legend:{position:'top'},
    
    datalabels: {
      color: '#ffffff',        
      font: {
        weight: 'bold',
        size: 12
      },
      formatter: (value: number) => value + '%'
    },

    tooltip:{
      callbacks:{
        label:(context)=>{

          const label=context.dataset.label;
          const percentage=context.raw as number;
          const index=context.dataIndex;

          const positiveCount=this.sourcePositiveCounts[index];
          const negativeCount=this.sourceNegativeCounts[index];

          if(label==='Positive'){
            return `Positive: ${positiveCount} (${percentage}%)`;
          }

          if(label==='Negative'){
            return `Negative: ${negativeCount} (${percentage}%)`;
          }

          return `${label}: ${percentage}%`;
        }
      }
    }
  }
};
  // end source wise sentiment

  // start country wise
countryChartData: ChartConfiguration<'pie'>['data']={
  labels:[],
  datasets:[
    {
      data:[],
      backgroundColor:[
        '#3f51b5',
        '#f44336',
        '#ff9800',
        '#4caf50',
        '#9c27b0'
      ]
    }
  ]
};

countryChartOptions: ChartConfiguration<'pie'>['options']={
  responsive:true,
  plugins:{
    legend:{
      position:'right'
    },
    tooltip:{
      callbacks:{
        label:(context)=>{
          const label=context.label;
          const value=context.raw as number;
          return `${label}: ${value} reviews`;
        }
      }
    },
    datalabels:{
      color:'#ffffff',
      font:{weight:'bold',size:14},
      formatter:(value,ctx)=>{
        const total = ctx.chart.data.datasets[0].data
          .reduce((a:any,b:any)=>a+b,0);

        const percent = ((value as number)/total*100).toFixed(1);
        return percent + '%';
      }
    }
  }
};
// end country wise
  ngOnInit(){

    this.productService.selectedProduct$
    .subscribe(productId=>{
      if(productId){
        this.loadDashboard(productId);
      }
    });

    this.productService.selectedComponent$
    .subscribe(componentId=>{
      if(componentId){
        this.loadComponentSentiment(componentId);
      }
    });

  }

  loadDashboard(productId:number){
    this.isInitialState = false;

    this.http
    .get<any>(`http://localhost:8082/api/dashboard/${productId}`)
    .subscribe(data=>{

      this.productName=data.productName;
      this.productImage=data.productImage;
      this.releasedDate=data.releasedDate;
      this.chipset=data.chipset;
      this.memory=data.memory;
      this.camera=data.camera;
      this.battery=data.battery;

      this.positive=data.positivePercentage;
      this.negative=data.negativePercentage;

      this.positiveReviewCount=data.positiveReviewCount;
      this.negativeReviewCount=data.negativeReviewCount;

      this.totalReviews=data.totalCount;

      this.productLoaded=true;
      this.componentLoaded=false;

      this.doughnutChartData.datasets[0].data=[
        this.positive,
        this.negative
      ];

      this.cd.detectChanges();
      this.chart?.update();

      this.loadComponentChart(productId);
      this.loadSourceChart(productId);
      this.loadCountryChart(productId);

    });

  }

  loadComponentChart(productId:number){

    this.http
    .get<any>(`http://localhost:8082/api/dashboard/${productId}/components`)
    .subscribe(data=>{

      const labels:string[]=[];
      const positive:number[]=[];
      const negative:number[]=[];
      const positiveCounts:number[]=[];
      const negativeCounts:number[]=[];

      let overallTotal = 0;

      Object.keys(data).forEach(component=>{

        const comp=data[component];

        labels.push(component.charAt(0).toUpperCase()+component.slice(1));

        positive.push(comp.positivePercentage);
        negative.push(comp.negativePercentage);

        positiveCounts.push(comp.positiveCount);
        negativeCounts.push(comp.negativeCount);

        overallTotal += comp.totalCount;

      });

      this.componentDataAvailable = overallTotal > 0;

      this.componentPositiveCounts=positiveCounts;
      this.componentNegativeCounts=negativeCounts;

      this.barChartData={
        labels:labels,
        datasets:[
          {label:'Positive',data:positive,backgroundColor:'#4caf50'},
          {label:'Negative',data:negative,backgroundColor:'#e53935'}
        ]
      };

      this.cd.detectChanges();
      this.chart?.update();

    });

  }

  loadComponentSentiment(componentId:number){
    this.isInitialState = false;
    
    this.http
    .get<any>(`http://localhost:8082/api/component-sentiment/${componentId}`)
    .subscribe(data=>{

      this.componentName=data.component
      ? data.component.charAt(0).toUpperCase()+data.component.slice(1)
      : '';

      this.positive=data.positivePercentage;
      this.negative=data.negativePercentage;

      this.positiveReviewCount=data.positiveCount;
      this.negativeReviewCount=data.negativeCount;

      this.totalReviews=data.totalCount;

      this.productLoaded=false;
      this.componentLoaded=true;

      this.doughnutChartData.datasets[0].data=[
        this.positive,
        this.negative
      ];

      this.cd.detectChanges();
      this.chart?.update();

    });

  }

  loadSourceChart(productId:number){

  this.http
  .get<any>(`http://localhost:8082/api/dashboard/${productId}/sources`)
  .subscribe(data=>{

    const labels:string[]=[];
    const positive:number[]=[];
    const negative:number[]=[];
    const positiveCounts:number[]=[];
    const negativeCounts:number[]=[];

    let total=0;

    Object.keys(data).forEach(source=>{

      const s=data[source];

      labels.push(source.charAt(0).toUpperCase()+source.slice(1));

      positive.push(s.positivePercentage);
      negative.push(s.negativePercentage);

      positiveCounts.push(s.positiveCount);
      negativeCounts.push(s.negativeCount);

      total += s.totalCount;

    });

    this.sourceDataAvailable = total > 0;

    this.sourcePositiveCounts = positiveCounts;
    this.sourceNegativeCounts = negativeCounts;

    this.sourceChartData={
      labels:labels,
      datasets:[
        {label:'Positive',data:positive,backgroundColor:'#4caf50',stack:'sentiment'},
        {label:'Negative',data:negative,backgroundColor:'#e53935',stack:'sentiment'}
      ]
    };

    this.cd.detectChanges();
    this.chart?.update();

  });

  }

  loadCountryChart(productId:number){

  this.http
  .get<any>(`http://localhost:8082/api/dashboard/${productId}/countries`)
  .subscribe(data=>{

    const labels:string[]=[];
    const counts:number[]=[];
    let total=0;

    Object.keys(data).forEach(country=>{

      labels.push(country);
      counts.push(data[country]);

      total += data[country];

    });

    this.countryDataAvailable = total > 0;

    this.countryChartData={
      labels:labels,
      datasets:[
        {
          data:counts,
          backgroundColor:[
            '#3f51b5',
            '#f44336',
            '#ff9800',
            '#4caf50',
            '#9c27b0'
          ]
        }
      ]
    };

    this.cd.detectChanges();
    this.chart?.update();

  });

}

}