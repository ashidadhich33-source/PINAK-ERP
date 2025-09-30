import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { settingsService } from '../../services/settingsService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  FileText, 
  Plus, 
  Edit, 
  Trash2, 
  Download, 
  Upload, 
  RefreshCw, 
  Save, 
  Eye,
  Settings,
  Receipt,
  FileInvoice,
  Tag,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react';

const PrintTemplates = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [showTemplateEditor, setShowTemplateEditor] = useState(false);
  const [templateContent, setTemplateContent] = useState('');

  // Template types
  const templateTypes = [
    {
      id: 'invoice',
      name: 'Invoice Template',
      icon: FileInvoice,
      description: 'Customer invoice template',
      defaultContent: `<!DOCTYPE html>
<html>
<head>
    <title>Invoice</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .company-info { margin-bottom: 20px; }
        .invoice-details { display: flex; justify-content: space-between; margin-bottom: 30px; }
        .items-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
        .items-table th, .items-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .items-table th { background-color: #f2f2f2; }
        .total-section { text-align: right; }
        .footer { margin-top: 50px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{company_name}}</h1>
        <p>{{company_address}}</p>
        <p>Phone: {{company_phone}} | Email: {{company_email}}</p>
    </div>
    
    <div class="invoice-details">
        <div>
            <h3>Bill To:</h3>
            <p>{{customer_name}}</p>
            <p>{{customer_address}}</p>
        </div>
        <div>
            <h3>Invoice Details:</h3>
            <p><strong>Invoice #:</strong> {{invoice_number}}</p>
            <p><strong>Date:</strong> {{invoice_date}}</p>
            <p><strong>Due Date:</strong> {{due_date}}</p>
        </div>
    </div>
    
    <table class="items-table">
        <thead>
            <tr>
                <th>Item</th>
                <th>Quantity</th>
                <th>Rate</th>
                <th>Amount</th>
            </tr>
        </thead>
        <tbody>
            {{#items}}
            <tr>
                <td>{{name}}</td>
                <td>{{quantity}}</td>
                <td>{{rate}}</td>
                <td>{{amount}}</td>
            </tr>
            {{/items}}
        </tbody>
    </table>
    
    <div class="total-section">
        <p><strong>Subtotal: {{subtotal}}</strong></p>
        <p><strong>Tax: {{tax_amount}}</strong></p>
        <p><strong>Total: {{total_amount}}</strong></p>
    </div>
    
    <div class="footer">
        <p>Thank you for your business!</p>
    </div>
</body>
</html>`
    },
    {
      id: 'receipt',
      name: 'Receipt Template',
      icon: Receipt,
      description: 'POS receipt template',
      defaultContent: `<!DOCTYPE html>
<html>
<head>
    <title>Receipt</title>
    <style>
        body { font-family: monospace; margin: 0; padding: 10px; width: 300px; }
        .header { text-align: center; margin-bottom: 20px; }
        .receipt-details { margin-bottom: 20px; }
        .items { margin-bottom: 20px; }
        .item { display: flex; justify-content: space-between; margin-bottom: 5px; }
        .total { border-top: 1px dashed #000; padding-top: 10px; margin-top: 10px; }
        .footer { margin-top: 20px; text-align: center; font-size: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>{{company_name}}</h2>
        <p>{{company_address}}</p>
        <p>Phone: {{company_phone}}</p>
    </div>
    
    <div class="receipt-details">
        <p><strong>Receipt #:</strong> {{receipt_number}}</p>
        <p><strong>Date:</strong> {{receipt_date}}</p>
        <p><strong>Cashier:</strong> {{cashier_name}}</p>
    </div>
    
    <div class="items">
        {{#items}}
        <div class="item">
            <span>{{name}} x {{quantity}}</span>
            <span>{{amount}}</span>
        </div>
        {{/items}}
    </div>
    
    <div class="total">
        <p><strong>Subtotal: {{subtotal}}</strong></p>
        <p><strong>Tax: {{tax_amount}}</strong></p>
        <p><strong>Total: {{total_amount}}</strong></p>
        <p><strong>Payment: {{payment_method}}</strong></p>
    </div>
    
    <div class="footer">
        <p>Thank you for your purchase!</p>
    </div>
</body>
</html>`
    },
    {
      id: 'label',
      name: 'Label Template',
      icon: Tag,
      description: 'Product label template',
      defaultContent: `<!DOCTYPE html>
<html>
<head>
    <title>Product Label</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 10px; width: 200px; }
        .label { border: 1px solid #000; padding: 10px; text-align: center; }
        .product-name { font-size: 14px; font-weight: bold; margin-bottom: 5px; }
        .product-code { font-size: 12px; color: #666; margin-bottom: 5px; }
        .price { font-size: 16px; font-weight: bold; color: #e74c3c; }
        .barcode { margin-top: 10px; }
    </style>
</head>
<body>
    <div class="label">
        <div class="product-name">{{product_name}}</div>
        <div class="product-code">SKU: {{product_sku}}</div>
        <div class="price">₹{{product_price}}</div>
        <div class="barcode">
            <img src="{{barcode_image}}" alt="Barcode" />
        </div>
    </div>
</body>
</html>`
    }
  ];

  // Fetch templates
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const templatesData = await settingsService.getPrintTemplates();
        setTemplates(templatesData);
      } catch (err) {
        setError(err.message);
        addNotification({
          type: 'danger',
          title: 'Error',
          message: err.message,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  // Handle template selection
  const handleTemplateSelect = async (templateType) => {
    try {
      setLoading(true);
      const template = await settingsService.getPrintTemplate(templateType);
      setSelectedTemplate(templateType);
      setTemplateContent(template.content || '');
      setShowTemplateEditor(true);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle save template
  const handleSaveTemplate = async () => {
    try {
      setSaving(true);
      await settingsService.updatePrintTemplate(selectedTemplate, templateContent);
      setShowTemplateEditor(false);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Template saved successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setSaving(false);
    }
  };

  // Handle reset template
  const handleResetTemplate = async (templateType) => {
    if (!window.confirm('Are you sure you want to reset this template to default?')) {
      return;
    }

    try {
      setSaving(true);
      await settingsService.resetPrintTemplate(templateType);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Template reset to default',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setSaving(false);
    }
  };

  // Handle preview template
  const handlePreviewTemplate = () => {
    const previewWindow = window.open('', '_blank', 'width=800,height=600');
    previewWindow.document.write(templateContent);
    previewWindow.document.close();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading templates..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Print Templates</h1>
          <p className="text-gray-600">Manage invoice, receipt, and label templates</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => window.location.reload()}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templateTypes.map((template) => {
          const Icon = template.icon;
          return (
            <div key={template.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Icon className="w-6 h-6 text-primary-600" />
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{template.name}</h3>
                  <p className="text-sm text-gray-500">{template.description}</p>
                </div>
              </div>
              
              <div className="space-y-3">
                <Button
                  onClick={() => handleTemplateSelect(template.id)}
                  className="w-full flex items-center justify-center space-x-2"
                >
                  <Edit className="w-4 h-4" />
                  <span>Edit Template</span>
                </Button>
                
                <Button
                  variant="outline"
                  onClick={() => handleResetTemplate(template.id)}
                  disabled={saving}
                  className="w-full flex items-center justify-center space-x-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Reset to Default</span>
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Template Editor Modal */}
      {showTemplateEditor && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowTemplateEditor(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        Edit {templateTypes.find(t => t.id === selectedTemplate)?.name}
                      </h3>
                      <p className="text-sm text-gray-500">Customize your print template</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowTemplateEditor(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <span className="sr-only">Close</span>
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Info className="w-4 h-4" />
                    <span>Use variables like {{company_name}}, {{customer_name}}, etc. in your template</span>
                  </div>
                  
                  <div className="border border-gray-300 rounded-lg">
                    <div className="bg-gray-50 px-4 py-2 border-b border-gray-300 flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Template Content</span>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handlePreviewTemplate}
                          className="flex items-center space-x-1"
                        >
                          <Eye className="w-4 h-4" />
                          <span>Preview</span>
                        </Button>
                      </div>
                    </div>
                    <textarea
                      value={templateContent}
                      onChange={(e) => setTemplateContent(e.target.value)}
                      rows={20}
                      className="w-full p-4 border-0 resize-none focus:ring-0 focus:outline-none"
                      placeholder="Enter your template content here..."
                    />
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={handleSaveTemplate}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Save Template
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowTemplateEditor(false)}
                  className="mt-3 w-full sm:mt-0 sm:w-auto"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Template Variables Help */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Settings className="w-6 h-6 text-primary-600" />
          <h3 className="text-lg font-medium text-gray-900">Available Variables</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2">Company Variables</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li><code>{{company_name}}</code> - Company name</li>
              <li><code>{{company_address}}</code> - Company address</li>
              <li><code>{{company_phone}}</code> - Company phone</li>
              <li><code>{{company_email}}</code> - Company email</li>
              <li><code>{{company_logo}}</code> - Company logo</li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2">Customer Variables</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li><code>{{customer_name}}</code> - Customer name</li>
              <li><code>{{customer_address}}</code> - Customer address</li>
              <li><code>{{customer_phone}}</code> - Customer phone</li>
              <li><code>{{customer_email}}</code> - Customer email</li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2">Transaction Variables</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li><code>{{invoice_number}}</code> - Invoice number</li>
              <li><code>{{invoice_date}}</code> - Invoice date</li>
              <li><code>{{total_amount}}</code> - Total amount</li>
              <li><code>{{tax_amount}}</code> - Tax amount</li>
              <li><code>{{subtotal}}</code> - Subtotal</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrintTemplates;