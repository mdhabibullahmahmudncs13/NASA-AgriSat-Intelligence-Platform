'use client';

import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface ThreeDVisualizationProps {
  className?: string;
  type: 'globe' | 'satellite' | 'chart' | 'particles';
  data?: any[];
}

export default function ThreeDVisualization({ className = '', type, data = [] }: ThreeDVisualizationProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;

    const svg = d3.select(svgRef.current);
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    svg.selectAll('*').remove();
    svg.attr('width', width).attr('height', height);

    // Create gradients for 3D effects
    const defs = svg.append('defs');
    
    // Realistic Earth ocean gradient matching reference image
    const earthGradient = defs.append('radialGradient')
      .attr('id', 'earthGradient')
      .attr('cx', '30%')
      .attr('cy', '30%');
    
    earthGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#4a90e2')
      .attr('stop-opacity', 1);
    
    earthGradient.append('stop')
      .attr('offset', '40%')
      .attr('stop-color', '#2563eb')
      .attr('stop-opacity', 0.95);
    
    earthGradient.append('stop')
      .attr('offset', '70%')
      .attr('stop-color', '#1e40af')
      .attr('stop-opacity', 0.9);
    
    earthGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#1e3a8a')
      .attr('stop-opacity', 0.85);

    // Cloud gradient for atmospheric layers
    const cloudGradient = defs.append('radialGradient')
      .attr('id', 'cloudGradient')
      .attr('cx', '40%')
      .attr('cy', '30%');
    
    cloudGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#ffffff')
      .attr('stop-opacity', 0.8);
    
    cloudGradient.append('stop')
      .attr('offset', '50%')
      .attr('stop-color', '#f0f9ff')
      .attr('stop-opacity', 0.4);
    
    cloudGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#e0f2fe')
      .attr('stop-opacity', 0.1);

    // Continent gradient matching reference Earth colors
    const continentGradient = defs.append('radialGradient')
      .attr('id', 'continentGradient')
      .attr('cx', '30%')
      .attr('cy', '30%');
    
    continentGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#8fbc8f')
      .attr('stop-opacity', 0.9);
    
    continentGradient.append('stop')
      .attr('offset', '50%')
      .attr('stop-color', '#6b8e23')
      .attr('stop-opacity', 0.85);
    
    continentGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#556b2f')
      .attr('stop-opacity', 0.8);

    // Gradient for satellite effect
    const satelliteGradient = defs.append('linearGradient')
      .attr('id', 'satelliteGradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '100%');
    
    satelliteGradient.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#10b981');
    
    satelliteGradient.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#059669');

    const g = svg.append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`);

    switch (type) {
      case 'globe':
        createGlobe(g, width, height);
        break;
      case 'satellite':
        createSatellite(g, width, height);
        break;
      case 'chart':
        create3DChart(g, width, height, data);
        break;
      case 'particles':
        createParticles(g, width, height);
        break;
    }

  }, [type, data]);

  const createGlobe = (g: d3.Selection<SVGGElement, unknown, null, undefined>, width: number, height: number) => {
    const radius = Math.min(width, height) * 0.3;
    
    // Main Earth globe with ocean colors
    const globe = g.append('circle')
      .attr('r', radius)
      .attr('fill', 'url(#earthGradient)')
      .attr('stroke', '#2563eb')
      .attr('stroke-width', 2)
      .attr('opacity', 0.95);

    // Add realistic continent shapes matching reference Earth image
    const continentGroup = g.append('g').attr('class', 'continents');
    
    // North America - positioned to match reference
    continentGroup.append('path')
      .attr('d', `M ${-radius * 0.5} ${-radius * 0.4} 
                  C ${-radius * 0.35} ${-radius * 0.6} ${-radius * 0.15} ${-radius * 0.55} ${-radius * 0.05} ${-radius * 0.5}
                  C ${radius * 0.1} ${-radius * 0.35} ${radius * 0.2} ${-radius * 0.15} ${radius * 0.15} ${radius * 0.0}
                  C ${radius * 0.05} ${radius * 0.1} ${-radius * 0.1} ${radius * 0.2} ${-radius * 0.25} ${radius * 0.05}
                  C ${-radius * 0.4} ${-radius * 0.1} ${-radius * 0.5} ${-radius * 0.25} ${-radius * 0.5} ${-radius * 0.4} Z`)
      .attr('fill', 'url(#continentGradient)')
      .attr('opacity', 0.85);
    
    // South America - elongated and positioned correctly
    continentGroup.append('path')
      .attr('d', `M ${-radius * 0.3} ${radius * 0.05}
                  C ${-radius * 0.2} ${radius * 0.0} ${-radius * 0.15} ${radius * 0.15} ${-radius * 0.17} ${radius * 0.3}
                  C ${-radius * 0.22} ${radius * 0.45} ${-radius * 0.28} ${radius * 0.6} ${-radius * 0.35} ${radius * 0.5}
                  C ${-radius * 0.4} ${radius * 0.35} ${-radius * 0.37} ${radius * 0.2} ${-radius * 0.3} ${radius * 0.05} Z`)
      .attr('fill', 'url(#continentGradient)')
      .attr('opacity', 0.8);
    
    // Africa - distinctive shape matching reference
    continentGroup.append('path')
      .attr('d', `M ${radius * 0.02} ${-radius * 0.15}
                  C ${radius * 0.12} ${-radius * 0.2} ${radius * 0.18} ${-radius * 0.1} ${radius * 0.16} ${radius * 0.05}
                  C ${radius * 0.18} ${radius * 0.2} ${radius * 0.14} ${radius * 0.35} ${radius * 0.08} ${radius * 0.5}
                  C ${radius * 0.03} ${radius * 0.45} ${-radius * 0.01} ${radius * 0.3} ${radius * 0.0} ${radius * 0.1}
                  C ${radius * 0.01} ${-radius * 0.05} ${radius * 0.02} ${-radius * 0.1} ${radius * 0.02} ${-radius * 0.15} Z`)
      .attr('fill', 'url(#continentGradient)')
      .attr('opacity', 0.75);
    
    // Europe - small but visible
    continentGroup.append('path')
      .attr('d', `M ${radius * 0.05} ${-radius * 0.3}
                  C ${radius * 0.12} ${-radius * 0.35} ${radius * 0.2} ${-radius * 0.33} ${radius * 0.25} ${-radius * 0.25}
                  C ${radius * 0.2} ${-radius * 0.2} ${radius * 0.15} ${-radius * 0.18} ${radius * 0.1} ${-radius * 0.2}
                  C ${radius * 0.07} ${-radius * 0.23} ${radius * 0.05} ${-radius * 0.27} ${radius * 0.05} ${-radius * 0.3} Z`)
      .attr('fill', 'url(#continentGradient)')
      .attr('opacity', 0.7);
    
    // Asia - large eastern continent
    continentGroup.append('path')
      .attr('d', `M ${radius * 0.2} ${-radius * 0.35}
                  C ${radius * 0.35} ${-radius * 0.4} ${radius * 0.5} ${-radius * 0.25} ${radius * 0.45} ${-radius * 0.1}
                  C ${radius * 0.47} ${radius * 0.05} ${radius * 0.4} ${radius * 0.2} ${radius * 0.3} ${radius * 0.25}
                  C ${radius * 0.25} ${radius * 0.15} ${radius * 0.23} ${radius * 0.0} ${radius * 0.2} ${-radius * 0.15}
                  C ${radius * 0.19} ${-radius * 0.25} ${radius * 0.2} ${-radius * 0.3} ${radius * 0.2} ${-radius * 0.35} Z`)
      .attr('fill', 'url(#continentGradient)')
      .attr('opacity', 0.65);
    
    // Australia - positioned in southern hemisphere
    continentGroup.append('ellipse')
      .attr('cx', radius * 0.35)
      .attr('cy', radius * 0.4)
      .attr('rx', radius * 0.1)
      .attr('ry', radius * 0.07)
      .attr('fill', 'url(#continentGradient)')
      .attr('opacity', 0.75);
    
    // Greenland - arctic region
    continentGroup.append('ellipse')
      .attr('cx', -radius * 0.15)
      .attr('cy', -radius * 0.45)
      .attr('rx', radius * 0.05)
      .attr('ry', radius * 0.08)
      .attr('fill', 'url(#continentGradient)')
      .attr('opacity', 0.65);
    
    // Antarctica - bottom ice cap
     continentGroup.append('ellipse')
       .attr('cx', 0)
       .attr('cy', radius * 0.75)
       .attr('rx', radius * 0.35)
       .attr('ry', radius * 0.06)
       .attr('fill', '#e6f3ff')
       .attr('opacity', 0.9);

    // Add subtle cloud layers for realistic atmosphere
    const cloudGroup = g.append('g').attr('class', 'clouds');
    
    // Cloud layer 1 - over Pacific (subtle)
    cloudGroup.append('ellipse')
      .attr('cx', -radius * 0.25)
      .attr('cy', -radius * 0.05)
      .attr('rx', radius * 0.15)
      .attr('ry', radius * 0.1)
      .attr('fill', 'url(#cloudGradient)')
      .attr('opacity', 0.3);
    
    // Cloud layer 2 - tropical band
    cloudGroup.append('ellipse')
      .attr('cx', radius * 0.05)
      .attr('cy', radius * 0.2)
      .attr('rx', radius * 0.2)
      .attr('ry', radius * 0.06)
      .attr('fill', 'url(#cloudGradient)')
      .attr('opacity', 0.25);

    // Create subtle latitude lines (like Earth's grid)
    for (let i = -60; i <= 60; i += 30) {
      const y = (i / 90) * radius * 0.8;
      const ellipseWidth = Math.cos((i * Math.PI) / 180) * radius * 1.8;
      
      g.append('ellipse')
        .attr('cx', 0)
        .attr('cy', y)
        .attr('rx', ellipseWidth)
        .attr('ry', 6)
        .attr('fill', 'none')
        .attr('stroke', '#1e40af')
        .attr('stroke-width', 0.8)
        .attr('opacity', 0.3)
        .attr('stroke-dasharray', '2,2');
    }

    // Create subtle longitude lines
    for (let i = 0; i < 6; i++) {
      const angle = (i * 30 * Math.PI) / 180;
      g.append('ellipse')
        .attr('cx', 0)
        .attr('cy', 0)
        .attr('rx', radius * Math.cos(angle))
        .attr('ry', radius)
        .attr('fill', 'none')
        .attr('stroke', '#1e40af')
        .attr('stroke-width', 0.8)
        .attr('opacity', 0.3)
        .attr('stroke-dasharray', '2,2')
        .attr('transform', `rotate(${i * 30})`);
    }

    // Add rotating animation to the entire Earth (globe + continents)
    const earthGroup = g.append('g').attr('class', 'rotating-earth');
    earthGroup.node()?.appendChild(globe.node()!);
    earthGroup.node()?.appendChild(continentGroup.node()!);
    
    earthGroup.transition()
      .duration(40000)
      .ease(d3.easeLinear)
      .attrTween('transform', () => {
        return (t: number) => `rotate(${t * 360})`;
      })
      .on('end', function repeat() {
        d3.select(this).transition()
          .duration(40000)
          .ease(d3.easeLinear)
          .attrTween('transform', () => {
            return (t: number) => `rotate(${t * 360})`;
          })
          .on('end', repeat);
      });

    // Add slower cloud rotation for atmospheric effect
    cloudGroup.transition()
      .duration(50000)
      .ease(d3.easeLinear)
      .attrTween('transform', () => {
        return (t: number) => `rotate(${t * 360})`;
      })
      .on('end', function repeatClouds() {
        d3.select(this).transition()
          .duration(50000)
          .ease(d3.easeLinear)
          .attrTween('transform', () => {
            return (t: number) => `rotate(${t * 360})`;
          })
          .on('end', repeatClouds);
      });

    // Add subtle atmospheric glow effect
    g.append('circle')
      .attr('r', radius * 1.02)
      .attr('fill', 'none')
      .attr('stroke', '#4a90e2')
      .attr('stroke-width', 2)
      .attr('opacity', 0.2);

    // Add very subtle outer atmosphere
    g.append('circle')
      .attr('r', radius * 1.08)
      .attr('fill', 'none')
      .attr('stroke', '#87ceeb')
      .attr('stroke-width', 1)
      .attr('opacity', 0.15);
  };

  const createSatellite = (g: d3.Selection<SVGGElement, unknown, null, undefined>, width: number, height: number) => {
    const size = Math.min(width, height) * 0.15;
    
    // Satellite body
    g.append('rect')
      .attr('x', -size / 2)
      .attr('y', -size / 3)
      .attr('width', size)
      .attr('height', size * 0.6)
      .attr('fill', 'url(#satelliteGradient)')
      .attr('stroke', '#059669')
      .attr('stroke-width', 2)
      .attr('rx', 5);

    // Solar panels
    g.append('rect')
      .attr('x', -size * 1.2)
      .attr('y', -size / 6)
      .attr('width', size * 0.4)
      .attr('height', size * 0.3)
      .attr('fill', '#1e40af')
      .attr('stroke', '#3b82f6')
      .attr('stroke-width', 1);

    g.append('rect')
      .attr('x', size * 0.8)
      .attr('y', -size / 6)
      .attr('width', size * 0.4)
      .attr('height', size * 0.3)
      .attr('fill', '#1e40af')
      .attr('stroke', '#3b82f6')
      .attr('stroke-width', 1);

    // Antenna
    g.append('line')
      .attr('x1', 0)
      .attr('y1', -size / 3)
      .attr('x2', 0)
      .attr('y2', -size * 0.8)
      .attr('stroke', '#10b981')
      .attr('stroke-width', 3);

    g.append('circle')
      .attr('cx', 0)
      .attr('cy', -size * 0.8)
      .attr('r', 4)
      .attr('fill', '#10b981');

    // Floating animation
    g.transition()
      .duration(3000)
      .ease(d3.easeSinInOut)
      .attr('transform', `translate(${width / 2}, ${height / 2 - 10})`)
      .transition()
      .duration(3000)
      .attr('transform', `translate(${width / 2}, ${height / 2 + 10})`)
      .on('end', function repeat() {
        d3.select(this)
          .transition()
          .duration(3000)
          .ease(d3.easeSinInOut)
          .attr('transform', `translate(${width / 2}, ${height / 2 - 10})`)
          .transition()
          .duration(3000)
          .attr('transform', `translate(${width / 2}, ${height / 2 + 10})`)
          .on('end', repeat);
      });
  };

  const create3DChart = (g: d3.Selection<SVGGElement, unknown, null, undefined>, width: number, height: number, data: any[]) => {
    const chartData = data.length > 0 ? data : [
      { label: 'Healthy', value: 75, color: '#10b981' },
      { label: 'Warning', value: 20, color: '#f59e0b' },
      { label: 'Critical', value: 5, color: '#ef4444' }
    ];

    const radius = Math.min(width, height) * 0.25;
    const pie = d3.pie<any>()
      .value(d => d.value)
      .sort(null)
      .startAngle(-Math.PI / 2); // Start from top
    
    const arc = d3.arc<any>()
      .innerRadius(radius * 0.5)
      .outerRadius(radius);
    
    const arc3D = d3.arc<any>()
      .innerRadius(radius * 0.5)
      .outerRadius(radius + 6);

    // Create chart container group (no rotation animation)
    const chartGroup = g.append('g')
      .attr('class', 'chart-container');

    const arcs = chartGroup.selectAll('.arc')
      .data(pie(chartData))
      .enter().append('g')
      .attr('class', 'arc')
      .style('cursor', 'pointer');

    // 3D shadow effect (bottom layer)
    arcs.append('path')
      .attr('d', arc)
      .attr('fill', (d: any) => d3.color(d.data.color)?.darker(2).toString() || '#000')
      .attr('transform', 'translate(3, 3)')
      .attr('opacity', 0.3);

    // Main pie slices
    const mainPaths = arcs.append('path')
      .attr('d', arc)
      .attr('fill', (d: any) => d.data.color)
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
      .style('filter', 'drop-shadow(2px 2px 4px rgba(0,0,0,0.3))')
      .on('mouseover', function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('d', arc3D)
          .style('filter', 'drop-shadow(3px 3px 6px rgba(0,0,0,0.4))');
      })
      .on('mouseout', function(event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('d', arc)
          .style('filter', 'drop-shadow(2px 2px 4px rgba(0,0,0,0.3))');
      });

    // Labels with better positioning
    arcs.append('text')
      .attr('transform', (d: any) => {
        const centroid = arc.centroid(d);
        return `translate(${centroid[0]}, ${centroid[1]})`;
      })
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', '#ffffff')
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .style('text-shadow', '1px 1px 2px rgba(0,0,0,0.8)')
      .text((d: any) => `${d.data.value}%`);

    // Add center label
    chartGroup.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', '#374151')
      .attr('font-size', '10px')
      .attr('font-weight', 'bold')
      .text('Crop Health');

    // Add simple legend below the chart
    const legendY = radius + 25;
    const legend = chartGroup.append('g')
      .attr('class', 'legend')
      .attr('transform', `translate(${-width * 0.15}, ${legendY})`);

    const legendItems = legend.selectAll('.legend-item')
      .data(chartData)
      .enter().append('g')
      .attr('class', 'legend-item')
      .attr('transform', (d, i) => `translate(${i * (width * 0.1)}, 0)`);

    legendItems.append('circle')
      .attr('r', 4)
      .attr('fill', d => d.color)
      .attr('stroke', '#fff')
      .attr('stroke-width', 1);

    legendItems.append('text')
      .attr('x', 0)
      .attr('y', 15)
      .attr('text-anchor', 'middle')
      .attr('fill', '#374151')
      .attr('font-size', '9px')
      .attr('font-weight', '500')
      .text(d => d.label);
  };

  const createParticles = (g: d3.Selection<SVGGElement, unknown, null, undefined>, width: number, height: number) => {
    const particles = Array.from({ length: 50 }, (_, i) => ({
      id: i,
      x: Math.random() * width - width / 2,
      y: Math.random() * height - height / 2,
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2,
      radius: Math.random() * 3 + 1,
      color: d3.interpolateViridis(Math.random())
    }));

    const particleElements = g.selectAll('.particle')
      .data(particles)
      .enter().append('circle')
      .attr('class', 'particle')
      .attr('r', d => d.radius)
      .attr('fill', d => d.color)
      .attr('opacity', 0.7);

    const animate = () => {
      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        
        if (p.x > width / 2 || p.x < -width / 2) p.vx *= -1;
        if (p.y > height / 2 || p.y < -height / 2) p.vy *= -1;
      });

      particleElements
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      requestAnimationFrame(animate);
    };

    animate();
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
}