import { GoogleGenAI } from "@google/genai";

/**
 * Generates a reference image for 3D modeling based on a user prompt.
 * Uses the 'gemini-3-pro-image-preview' (Nano Banana Pro) model.
 */
export const generateReferenceImage = async (userPrompt: string): Promise<string> => {
  // Initialize the client inside the function to ensure the latest API_KEY is used
  // after the user selects it via the UI.
  // The API key is available via process.env.API_KEY which is injected automatically.
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

  // Engineered prompt to simulate a 3D design expert's requirement
  const engineeredPrompt = `
    You are generating a visual reference for a professional 3D design expert. 
    The expert needs to model the following object in a 3D application (like Blender, Maya, or ZBrush) based strictly on the image you provide: "${userPrompt}".

    Generate a high-fidelity, photorealistic image that acts as the perfect source material for this 3D modeling task.
    
    CRITICAL VISUAL REQUIREMENTS:
    1.  **Perspective**: Provide a clear, descriptive angle (orthographic or distinct 3/4 view) that reveals the most structural information about the object's volume and silhouette.
    2.  **Lighting**: Use neutral, studio-soft lighting. Avoid harsh shadows or over-exposed highlights that hide surface details. The geometry must be readable.
    3.  **Background**: A solid, neutral matte background (grey or white) to ensure easy segmentation.
    4.  **Detail**: Focus on structural clarity over artistic atmosphere. Textures and materials should be distinct to inform the shading process later.
    5.  **Completeness**: Ensure the entire object is within the frame; do not crop off essential parts.
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-image-preview',
      contents: {
        parts: [
          { text: engineeredPrompt }
        ]
      },
      config: {
        imageConfig: {
          aspectRatio: "1:1",
          imageSize: "1K"
        }
      }
    });

    // Iterate through parts to find the image data
    if (response.candidates && response.candidates[0].content.parts) {
      for (const part of response.candidates[0].content.parts) {
        if (part.inlineData) {
          const base64EncodeString = part.inlineData.data;
          const mimeType = part.inlineData.mimeType || 'image/png';
          return `data:${mimeType};base64,${base64EncodeString}`;
        }
      }
    }

    throw new Error("No image data found in the response.");

  } catch (error) {
    console.error("Error generating image:", error);
    throw error;
  }
};