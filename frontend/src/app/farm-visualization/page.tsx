'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import ProtectedRoute from '@/components/ProtectedRoute';

interface CropData {
  id: string;
  type: string;
  yield: number;
  health: string;
  growthStage: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

interface WeatherData {
  temperature: number;
  humidity: number;
  precipitation: number;
  windSpeed: number;
}

interface FarmerData {
  currentTask: string;
  location: { x: number; y: number };
  tool: string;
}

export default function FarmVisualizationPage() {
  const svgRef = useRef<SVGSVGElement>(null);
  const animationRef = useRef<number>();
  const isPausedRef = useRef(false);

  // Sample agricultural data
  const cropData: CropData[] = [
    { id: 'corn1', type: 'Corn', yield: 85, health: 'Excellent', growthStage: 'Mature', x: 100, y: 400, width: 150, height: 80 },
    { id: 'wheat1', type: 'Wheat', yield: 92, health: 'Good', growthStage: 'Flowering', x: 300, y: 420, width: 120, height: 60 },
    { id: 'soy1', type: 'Soybeans', yield: 78, health: 'Fair', growthStage: 'Vegetative', x: 500, y: 410, width: 140, height: 70 },
    { id: 'tomato1', type: 'Tomatoes', yield: 95, health: 'Excellent', growthStage: 'Fruiting', x: 700, y: 430, width: 100, height: 50 }
  ];

  const weatherData: WeatherData = {
    temperature: 24,
    humidity: 65,
    precipitation: 15,
    windSpeed: 8
  };

  const farmerData: FarmerData = {
    currentTask: 'Inspecting crops',
    location: { x: 200, y: 450 },
    tool: 'Inspection tablet'
  };

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const width = 1000;
    const height = 600;

    svg.attr('width', width).attr('height', height);
    svg.selectAll('*').remove();

    // Create gradients
    const defs = svg.append('defs');
    
    // Sky gradient
    const skyGradient = defs.append('linearGradient')
      .attr('id', 'skyGradient')
      .attr('x1', '0%').attr('y1', '0%')
      .attr('x2', '0%').attr('y2', '100%');
    
    skyGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#87CEEB');
    
    skyGradient.append('stop')
      .attr('offset', '70%')
      .attr('stop-color', '#E0F6FF');
    
    skyGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#98FB98');

    // Ground gradient
    const groundGradient = defs.append('linearGradient')
      .attr('id', 'groundGradient')
      .attr('x1', '0%').attr('y1', '0%')
      .attr('x2', '0%').attr('y2', '100%');
    
    groundGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#90EE90');
    
    groundGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#228B22');

    // Sun glow filter
    const sunGlow = defs.append('filter')
      .attr('id', 'sunGlow')
      .attr('x', '-50%').attr('y', '-50%')
      .attr('width', '200%').attr('height', '200%');
    
    sunGlow.append('feGaussianBlur')
      .attr('stdDeviation', '3')
      .attr('result', 'coloredBlur');
    
    const feMerge = sunGlow.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Draw sky
    svg.append('rect')
      .attr('width', width)
      .attr('height', height * 0.7)
      .attr('fill', 'url(#skyGradient)');

    // Draw ground
    svg.append('rect')
      .attr('y', height * 0.7)
      .attr('width', width)
      .attr('height', height * 0.3)
      .attr('fill', 'url(#groundGradient)');

    // Draw rolling hills
    const hillPath = d3.line<[number, number]>()
      .x(d => d[0])
      .y(d => d[1])
      .curve(d3.curveBasis);

    const hillPoints: [number, number][] = [
      [0, height * 0.75],
      [width * 0.2, height * 0.72],
      [width * 0.4, height * 0.74],
      [width * 0.6, height * 0.71],
      [width * 0.8, height * 0.73],
      [width, height * 0.72]
    ];

    svg.append('path')
      .datum(hillPoints)
      .attr('d', hillPath)
      .attr('fill', '#32CD32')
      .attr('opacity', 0.8);

    // Draw sun
    const sun = svg.append('g')
      .attr('transform', 'translate(150, 100)');
    
    sun.append('circle')
      .attr('r', 40)
      .attr('fill', '#FFD700')
      .attr('filter', 'url(#sunGlow)');

    // Draw sun rays
    const rayData = d3.range(8).map(i => ({
      angle: (i * 45) * Math.PI / 180,
      length: 60
    }));

    sun.selectAll('.ray')
      .data(rayData)
      .enter()
      .append('line')
      .attr('class', 'ray')
      .attr('x1', d => Math.cos(d.angle) * 45)
      .attr('y1', d => Math.sin(d.angle) * 45)
      .attr('x2', d => Math.cos(d.angle) * d.length)
      .attr('y2', d => Math.sin(d.angle) * d.length)
      .attr('stroke', '#FFD700')
      .attr('stroke-width', 3)
      .attr('opacity', 0.7);

    // Create clouds
    const cloudData = [
      { x: 300, y: 80, scale: 1 },
      { x: 600, y: 120, scale: 0.8 },
      { x: 850, y: 90, scale: 1.2 }
    ];

    function createCloud(g: d3.Selection<SVGGElement, any, any, any>) {
      const cloudPath = 'M25,60 Q25,25 55,25 Q85,10 115,25 Q145,25 145,60 Q135,85 105,85 Q75,100 45,85 Q25,85 25,60 Z';
      return g.append('path')
        .attr('d', cloudPath)
        .attr('fill', 'white')
        .attr('opacity', 0.9)
        .attr('stroke', '#E6E6FA')
        .attr('stroke-width', 1);
    }

    const clouds = svg.selectAll('.cloud')
      .data(cloudData)
      .enter()
      .append('g')
      .attr('class', 'cloud')
      .attr('transform', d => `translate(${d.x}, ${d.y}) scale(${d.scale})`);

    clouds.each(function() {
      createCloud(d3.select(this));
    });

    // Add cloud hover interaction
    clouds
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this).transition().duration(200).attr('opacity', 0.8);
        
        // Show weather tooltip
        const tooltip = svg.append('g')
          .attr('class', 'weather-tooltip')
          .attr('transform', `translate(${d.x + 50}, ${d.y - 20})`);
        
        const rect = tooltip.append('rect')
          .attr('width', 180)
          .attr('height', 80)
          .attr('fill', 'rgba(0,0,0,0.8)')
          .attr('rx', 5);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 20)
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text(`Temperature: ${weatherData.temperature}°C`);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 35)
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text(`Humidity: ${weatherData.humidity}%`);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 50)
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text(`Precipitation: ${weatherData.precipitation}mm`);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 65)
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text(`Wind: ${weatherData.windSpeed} km/h`);
      })
      .on('mouseout', function() {
        d3.select(this).transition().duration(200).attr('opacity', 1);
        svg.selectAll('.weather-tooltip').remove();
      });

    // Draw farm buildings
    const barn = svg.append('g')
      .attr('transform', 'translate(800, 300)');
    
    // Barn body
    barn.append('rect')
      .attr('width', 80)
      .attr('height', 60)
      .attr('fill', '#8B4513');
    
    // Barn roof
    barn.append('polygon')
      .attr('points', '0,0 40,-20 80,0')
      .attr('fill', '#654321');
    
    // Barn door
    barn.append('rect')
      .attr('x', 30)
      .attr('y', 20)
      .attr('width', 20)
      .attr('height', 40)
      .attr('fill', '#654321');

    // Draw crop fields
    const cropGroups = svg.selectAll('.crop-field')
      .data(cropData)
      .enter()
      .append('g')
      .attr('class', 'crop-field')
      .attr('transform', d => `translate(${d.x}, ${d.y})`);

    // Field backgrounds
    cropGroups.append('rect')
      .attr('width', d => d.width)
      .attr('height', d => d.height)
      .attr('fill', '#90EE90')
      .attr('opacity', 0.3)
      .attr('stroke', '#228B22')
      .attr('stroke-width', 2)
      .attr('rx', 5);

    // Draw crop rows
    cropGroups.each(function(d) {
      const group = d3.select(this);
      const rows = 4;
      const plantsPerRow = 8;
      
      for (let row = 0; row < rows; row++) {
        for (let plant = 0; plant < plantsPerRow; plant++) {
          const x = (plant * d.width / plantsPerRow) + 10;
          const y = (row * d.height / rows) + 15;
          
          // Plant representation
          group.append('circle')
            .attr('cx', x)
            .attr('cy', y)
            .attr('r', 3)
            .attr('fill', d.health === 'Excellent' ? '#228B22' : 
                         d.health === 'Good' ? '#32CD32' : '#90EE90')
            .attr('class', 'plant')
            .style('cursor', 'pointer');
        }
      }
    });

    // Add crop field interactions
    cropGroups
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        d3.select(this).select('rect').transition().duration(200).attr('opacity', 0.6);
        
        // Show crop tooltip
        const tooltip = svg.append('g')
          .attr('class', 'crop-tooltip')
          .attr('transform', `translate(${d.x + d.width + 10}, ${d.y})`);
        
        const rect = tooltip.append('rect')
          .attr('width', 150)
          .attr('height', 100)
          .attr('fill', 'rgba(0,0,0,0.8)')
          .attr('rx', 5);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 20)
          .attr('fill', 'white')
          .attr('font-size', '14px')
          .attr('font-weight', 'bold')
          .text(d.type);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 40)
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text(`Yield: ${d.yield}%`);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 55)
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text(`Health: ${d.health}`);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 70)
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text(`Stage: ${d.growthStage}`);
      })
      .on('mouseout', function() {
        d3.select(this).select('rect').transition().duration(200).attr('opacity', 0.3);
        svg.selectAll('.crop-tooltip').remove();
      });

    // Create farmer
    const farmer = svg.append('g')
      .attr('class', 'farmer')
      .attr('transform', `translate(${farmerData.location.x}, ${farmerData.location.y})`);

    // Farmer body
    farmer.append('circle')
      .attr('r', 8)
      .attr('fill', '#DEB887');
    
    // Farmer hat
    farmer.append('circle')
      .attr('cy', -5)
      .attr('r', 6)
      .attr('fill', '#8B4513');
    
    // Farmer tool
    farmer.append('line')
      .attr('x1', 10)
      .attr('y1', -5)
      .attr('x2', 20)
      .attr('y2', -15)
      .attr('stroke', '#654321')
      .attr('stroke-width', 3);

    // Add farmer interaction
    farmer
      .style('cursor', 'pointer')
      .on('click', function() {
        // Show farmer info
        const tooltip = svg.append('g')
          .attr('class', 'farmer-tooltip')
          .attr('transform', `translate(${farmerData.location.x + 30}, ${farmerData.location.y - 50})`);
        
        const rect = tooltip.append('rect')
          .attr('width', 160)
          .attr('height', 70)
          .attr('fill', 'rgba(0,0,0,0.8)')
          .attr('rx', 5);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 20)
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text(`Task: ${farmerData.currentTask}`);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 40)
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text(`Tool: ${farmerData.tool}`);
        
        tooltip.append('text')
          .attr('x', 10)
          .attr('y', 60)
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text('Click elsewhere to close');
        
        // Remove tooltip on next click
        svg.on('click.farmer', function() {
          svg.selectAll('.farmer-tooltip').remove();
          svg.on('click.farmer', null);
        });
      });

    // Animation variables
    let cloudOffset = 0;
    let farmerOffset = 0;
    let plantSway = 0;

    function animate() {
      if (isPausedRef.current) {
        animationRef.current = requestAnimationFrame(animate);
        return;
      }

      // Animate clouds
      cloudOffset += 0.2;
      clouds.attr('transform', (d, i) => {
        const newX = (d.x + cloudOffset + i * 100) % (width + 200) - 100;
        return `translate(${newX}, ${d.y}) scale(${d.scale})`;
      });

      // Animate farmer walking
      farmerOffset += 0.3;
      const farmerX = (farmerData.location.x + farmerOffset) % (width - 100) + 50;
      farmer.attr('transform', `translate(${farmerX}, ${farmerData.location.y})`);

      // Animate plant swaying
      plantSway += 0.05;
      svg.selectAll('.plant')
        .attr('transform', function() {
          const sway = Math.sin(plantSway + Math.random() * 2) * 1;
          return `translate(${sway}, 0)`;
        });

      animationRef.current = requestAnimationFrame(animate);
    }

    // Start animation
    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  const toggleAnimation = () => {
    isPausedRef.current = !isPausedRef.current;
  };

  return (
    <ProtectedRoute>
      <div className="px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="heading-primary mb-4">Interactive Farm Visualization</h1>
          <p className="text-xl text-gray-600 mb-6">
            Explore your farm with real-time data visualization. Hover over elements to see detailed information.
          </p>
          
          <div className="flex justify-center space-x-4 mb-6">
            <button
              onClick={toggleAnimation}
              className="btn-primary"
            >
              {isPausedRef.current ? 'Resume' : 'Pause'} Animation
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 text-sm">
            <div className="card">
              <h3 className="font-semibold mb-2">Instructions</h3>
              <ul className="text-left space-y-1">
                <li>• Hover over clouds for weather data</li>
                <li>• Hover over crop fields for yield info</li>
                <li>• Click on farmer for task details</li>
              </ul>
            </div>
            
            <div className="card">
              <h3 className="font-semibold mb-2">Current Weather</h3>
              <div className="text-left space-y-1">
                <div>Temperature: 24°C</div>
                <div>Humidity: 65%</div>
                <div>Wind: 8 km/h</div>
              </div>
            </div>
            
            <div className="card">
              <h3 className="font-semibold mb-2">Farm Status</h3>
              <div className="text-left space-y-1">
                <div>Active Fields: 4</div>
                <div>Average Yield: 87.5%</div>
                <div>Health Status: Good</div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <div className="border-2 border-gray-300 rounded-lg overflow-hidden shadow-lg">
            <svg ref={svgRef} className="block"></svg>
          </div>
        </div>

        <div className="mt-8 text-center">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="text-2xl font-bold text-green-600">4</div>
              <div className="text-sm text-gray-600">Active Fields</div>
            </div>
            <div className="card">
              <div className="text-2xl font-bold text-blue-600">87.5%</div>
              <div className="text-sm text-gray-600">Avg Yield</div>
            </div>
            <div className="card">
              <div className="text-2xl font-bold text-yellow-600">24°C</div>
              <div className="text-sm text-gray-600">Temperature</div>
            </div>
            <div className="card">
              <div className="text-2xl font-bold text-purple-600">Good</div>
              <div className="text-sm text-gray-600">Overall Health</div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}