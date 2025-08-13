'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface FarmBackgroundProps {
  className?: string;
  opacity?: number;
}

export default function FarmBackground({ className = '', opacity = 0.3 }: FarmBackgroundProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const width = 1200;
    const height = 800;

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

    // Create main background
    svg.append('rect')
      .attr('width', width)
      .attr('height', height * 0.7)
      .attr('fill', 'url(#skyGradient)');

    // Ground
    svg.append('rect')
      .attr('y', height * 0.7)
      .attr('width', width)
      .attr('height', height * 0.3)
      .attr('fill', 'url(#groundGradient)');

    // Create animated clouds
    const cloudData = [
      { x: 100, y: 80, size: 1, speed: 0.3 },
      { x: 300, y: 120, size: 0.8, speed: 0.2 },
      { x: 600, y: 60, size: 1.2, speed: 0.4 },
      { x: 900, y: 100, size: 0.9, speed: 0.25 }
    ];

    const clouds = svg.selectAll('.cloud')
      .data(cloudData)
      .enter()
      .append('g')
      .attr('class', 'cloud')
      .attr('transform', d => `translate(${d.x}, ${d.y}) scale(${d.size})`);

    // Cloud shape
    clouds.each(function() {
      const cloud = d3.select(this);
      
      cloud.append('ellipse')
        .attr('cx', 0).attr('cy', 0)
        .attr('rx', 25).attr('ry', 15)
        .attr('fill', '#FFFFFF')
        .attr('opacity', 0.8);
      
      cloud.append('ellipse')
        .attr('cx', -15).attr('cy', -5)
        .attr('rx', 20).attr('ry', 12)
        .attr('fill', '#FFFFFF')
        .attr('opacity', 0.8);
      
      cloud.append('ellipse')
        .attr('cx', 15).attr('cy', -3)
        .attr('rx', 18).attr('ry', 10)
        .attr('fill', '#FFFFFF')
        .attr('opacity', 0.8);
    });

    // Create crop fields
    const cropFields = [
      { x: 150, y: height * 0.75, width: 180, height: 100, color: '#32CD32' },
      { x: 400, y: height * 0.78, width: 160, height: 80, color: '#228B22' },
      { x: 650, y: height * 0.76, width: 170, height: 90, color: '#90EE90' },
      { x: 900, y: height * 0.77, width: 150, height: 85, color: '#98FB98' }
    ];

    cropFields.forEach(field => {
      const fieldGroup = svg.append('g');
      
      // Field background
      fieldGroup.append('rect')
        .attr('x', field.x)
        .attr('y', field.y)
        .attr('width', field.width)
        .attr('height', field.height)
        .attr('fill', field.color)
        .attr('opacity', 0.6)
        .attr('rx', 5);
      
      // Crop rows
      for (let i = 0; i < 4; i++) {
        fieldGroup.append('line')
          .attr('x1', field.x + 10)
          .attr('y1', field.y + 20 + i * 20)
          .attr('x2', field.x + field.width - 10)
          .attr('y2', field.y + 20 + i * 20)
          .attr('stroke', '#006400')
          .attr('stroke-width', 2)
          .attr('opacity', 0.7);
      }
    });

    // Add a simple farmer figure
    const farmer = svg.append('g')
      .attr('transform', 'translate(250, 580)');
    
    // Farmer body
    farmer.append('circle')
      .attr('cx', 0).attr('cy', -30)
      .attr('r', 8)
      .attr('fill', '#FFE4B5'); // Head
    
    farmer.append('rect')
      .attr('x', -6).attr('y', -22)
      .attr('width', 12).attr('height', 25)
      .attr('fill', '#4169E1'); // Body
    
    farmer.append('rect')
      .attr('x', -8).attr('y', 3)
      .attr('width', 6).attr('height', 15)
      .attr('fill', '#8B4513'); // Left leg
    
    farmer.append('rect')
      .attr('x', 2).attr('y', 3)
      .attr('width', 6).attr('height', 15)
      .attr('fill', '#8B4513'); // Right leg

    // Add some trees in the background
    const trees = [
      { x: 50, y: height * 0.65 },
      { x: 1100, y: height * 0.68 },
      { x: 1150, y: height * 0.63 }
    ];

    trees.forEach(tree => {
      const treeGroup = svg.append('g')
        .attr('transform', `translate(${tree.x}, ${tree.y})`);
      
      // Tree trunk
      treeGroup.append('rect')
        .attr('x', -5).attr('y', 0)
        .attr('width', 10).attr('height', 40)
        .attr('fill', '#8B4513');
      
      // Tree foliage
      treeGroup.append('circle')
        .attr('cx', 0).attr('cy', -10)
        .attr('r', 25)
        .attr('fill', '#228B22');
    });

    // Animation function
    const animate = () => {
      // Animate clouds
      svg.selectAll('.cloud')
        .each(function(d: any) {
          const cloud = d3.select(this);
          const currentTransform = cloud.attr('transform');
          const match = currentTransform.match(/translate\(([-\d.]+),\s*([-\d.]+)\)/);
          
          if (match) {
            let x = parseFloat(match[1]);
            const y = parseFloat(match[2]);
            
            x += d.speed;
            if (x > width + 50) x = -50;
            
            cloud.attr('transform', `translate(${x}, ${y}) scale(${d.size})`);
          }
        });
      
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <div className={`absolute inset-0 overflow-hidden ${className}`} style={{ opacity }}>
      <svg 
        ref={svgRef} 
        className="w-full h-full object-cover"
        preserveAspectRatio="xMidYMid slice"
      />
    </div>
  );
}