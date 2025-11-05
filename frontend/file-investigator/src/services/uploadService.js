const API_BASE_URL = process.env.BACKEND_URL || 'http://localhost:5001';

/**
 * Create a datastore for a file
 * @param {string} fileName - The file name to create datastore for
 * @returns {Promise<Object>} - Response with datastore information including display_name
 */
export const createDatastore = async (fileName) => {
  try {
    // Generate a unique datastore ID from filename (remove extension and special chars)
    const datastoreId = `ds_${fileName.replace(/[^a-zA-Z0-9]/g, '_')}_${Date.now()}`;


    const response = await fetch(`${API_BASE_URL}/api/vertex/create-datastore`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        datastore_name: datastoreId,
        display_name: fileName
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        message: 'Datastore creation failed',
      }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      data: {
        datastoreId: data.datastore_id,
        displayName: data.display_name,
        datastoreName: data.datastore_name
      }
    };
  } catch (error) {
    console.error('Create datastore error:', error);
    return {
      success: false,
      error: error.message || 'Failed to create datastore',
    };
  }
};

/**
 * Upload a file to the backend API
 * @param {File} file - The file to upload
 * @returns {Promise<Object>} - Response from the API with file information
 */
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {

    const response = await fetch(`${API_BASE_URL}/api/storage/signed-url?fileName=${file.name}&contentType=${file.type}`);

    console.log('signedUrl received:' + response);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const jsonResp = await response.json();

    console.log('jsonResp:' + jsonResp);

    const url = jsonResp.signedUrl;
    const actualFileName = jsonResp.fileName || file.name; // Use the actual fileName from backend
    
    console.log('uploading file to:' + url);
    console.log('file type:' + file.type);
    console.log('file name:' + file.name);
    console.log('actual file name:' + actualFileName);
    const upload = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': file.type,
      },
      body: file,
    });
  
    if (!upload.ok) {
      throw new Error('Upload failed.');
    }
  
    console.log('✅ File uploaded to GCS successfully');
    
    // Create datastore for the uploaded file (MUST succeed before returning)
    console.log('📦 Creating datastore for file...');
    const datastoreResult = await createDatastore(actualFileName.toLowerCase());
    
    if (!datastoreResult.success) {
      const error = `Datastore creation failed: ${datastoreResult.error}`;
      console.error('❌', error);
      throw new Error(error);
    }
    
    console.log('✅ Datastore created successfully');
    
    // Save file information to MongoDB
    console.log('💾 Saving file information to database...');
    const saveFileResponse = await fetch(`${API_BASE_URL}/api/files`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_name: actualFileName,
        datastore_id: datastoreResult.data.datastoreId
      })
    });
    
    if (!saveFileResponse.ok) {
      const errorData = await saveFileResponse.json().catch(() => ({
        message: 'Failed to save file to database',
      }));
      console.error('⚠️ Warning: File uploaded but database save failed:', errorData.error);
      // Don't throw error here - file is uploaded successfully
    } else {
      console.log('✅ File information saved to database');
    }
    
    console.log('🎉 Upload process complete!');
    
    return {
      success: true,
      data: {
        fileName: actualFileName,
        contentType: file.type,
        datastore: datastoreResult.data
      },
    };
      
  } catch (error) {
    console.error('Upload error:', error);
    return {
      success: false,
      error: error.message || 'Failed to upload file',
    };
  }
};

/**
 * Index a file in the datastore
 * @param {string} fileName - The name of the file to index
 * @param {string} datastoreDisplayName - The display_name of the datastore to index into
 * @returns {Promise<Object>} - Response from the API
 */
export const indexFile = async (fileName, datastoreDisplayName) => {
  try {
    if (!datastoreDisplayName) {
      throw new Error('Datastore display name is required for indexing');
    }

    const response = await fetch(`${API_BASE_URL}/api/vertex/import-document`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_name: fileName,
        datastore_name: datastoreDisplayName
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        message: 'Indexing failed',
      }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      data: data,
    };
  } catch (error) {
    console.error('Index file error:', error);
    return {
      success: false,
      error: error.message || 'Failed to index file',
    };
  }
};

/**
 * Mark a file as indexed in the database
 * @param {string} fileId - The MongoDB _id of the file
 * @param {boolean} indexed - Whether the file is indexed (default: true)
 * @returns {Promise<Object>} - Response from the API
 */
export const updateFileIndexStatus = async (fileId, indexed = true) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/files/${fileId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        indexed: indexed
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        message: 'Failed to update file status',
      }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      data: data,
    };
  } catch (error) {
    console.error('Update file status error:', error);
    return {
      success: false,
      error: error.message || 'Failed to update file status',
    };
  }
};

