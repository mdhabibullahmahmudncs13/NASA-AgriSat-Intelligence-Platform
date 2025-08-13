'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Field {
  id: string;
  name: string;
  cropType: string;
  areaHectares: number;
  plantingDate: string;
  expectedHarvest: string;
  growthStage: string;
  healthScore: number;
  status: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
}

export default function FieldsPage() {
  const [fields, setFields] = useState<Field[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCrop, setFilterCrop] = useState('all');

  useEffect(() => {
    // Mock data - replace with actual API call
    const mockFields: Field[] = [
      {
        id: '1',
        name: 'North Field A-12',
        cropType: 'wheat',
        areaHectares: 25.5,
        plantingDate: '2024-03-15',
        expectedHarvest: '2024-08-20',
        growthStage: 'vegetative',
        healthScore: 87,
        status: 'good'
      },
      {
        id: '2',
        name: 'South Field B-7',
        cropType: 'corn',
        areaHectares: 18.2,
        plantingDate: '2024-04-01',
        expectedHarvest: '2024-09-15',
        growthStage: 'reproductive',
        healthScore: 65,
        status: 'fair'
      },
      {
        id: '3',
        name: 'East Field C-3',
        cropType: 'soybean',
        areaHectares: 32.1,
        plantingDate: '2024-03-20',
        expectedHarvest: '2024-08-30',
        growthStage: 'maturation',
        healthScore: 92,
        status: 'excellent'
      },
      {
        id: '4',
        name: 'West Field D-9',
        cropType: 'rice',
        areaHectares: 15.8,
        plantingDate: '2024-04-10',
        expectedHarvest: '2024-09-25',
        growthStage: 'vegetative',
        healthScore: 45,
        status: 'poor'
      }
    ];

    setTimeout(() => {
      setFields(mockFields);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'bg-success-100 text-success-800';
      case 'good': return 'bg-primary-100 text-primary-800';
      case 'fair': return 'bg-warning-100 text-warning-800';
      case 'poor': return 'bg-danger-100 text-danger-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredFields = fields.filter(field => {
    const matchesSearch = field.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         field.cropType.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCrop = filterCrop === 'all' || field.cropType === filterCrop;
    return matchesSearch && matchesCrop;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="px-4 py-6">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Fields Management</h1>
            <p className="text-gray-600">Monitor and manage your agricultural fields</p>
          </div>
          <button className="btn-primary">
            Add New Field
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search fields..."
              className="input-field"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="sm:w-48">
            <select
              className="input-field"
              value={filterCrop}
              onChange={(e) => setFilterCrop(e.target.value)}
            >
              <option value="all">All Crops</option>
              <option value="wheat">Wheat</option>
              <option value="corn">Corn</option>
              <option value="rice">Rice</option>
              <option value="soybean">Soybean</option>
              <option value="cotton">Cotton</option>
            </select>
          </div>
        </div>
      </div>

      {/* Fields Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredFields.map((field) => (
          <div key={field.id} className="card hover:shadow-md transition-shadow duration-200">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{field.name}</h3>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(field.status)}`}>
                {field.status}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Crop Type:</span>
                <span className="text-sm font-medium text-gray-900 capitalize">{field.cropType}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Area:</span>
                <span className="text-sm font-medium text-gray-900">{field.areaHectares} ha</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Growth Stage:</span>
                <span className="text-sm font-medium text-gray-900 capitalize">{field.growthStage}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Health Score:</span>
                <span className="text-sm font-medium text-gray-900">{field.healthScore}%</span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    field.healthScore >= 80 ? 'bg-success-500' :
                    field.healthScore >= 60 ? 'bg-warning-500' : 'bg-danger-500'
                  }`}
                  style={{ width: `${field.healthScore}%` }}
                ></div>
              </div>
              
              <div className="flex justify-between text-xs text-gray-500">
                <span>Planted: {new Date(field.plantingDate).toLocaleDateString()}</span>
                <span>Harvest: {new Date(field.expectedHarvest).toLocaleDateString()}</span>
              </div>
            </div>

            <div className="mt-6 flex space-x-2">
              <Link 
                href={`/fields/${field.id}`}
                className="flex-1 text-center btn-primary text-sm py-2"
              >
                View Details
              </Link>
              <button className="flex-1 btn-secondary text-sm py-2">
                Edit Field
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredFields.length === 0 && (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No fields found</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating a new field.</p>
          <div className="mt-6">
            <button className="btn-primary">
              Add New Field
            </button>
          </div>
        </div>
      )}
    </div>
  );
}