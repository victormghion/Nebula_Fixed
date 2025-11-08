import express from 'express';
import cors from 'cors';
import { GoogleGenerativeAI } from '@google/generative-ai';

// --- Configuração ---
const app = express();
const port = process.env.PORT || 3000;

// Carrega a Chave da API (do Render, não daqui!)
const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

// --- Middlewares ---
app.use(express.json()); // Permite que o servidor entenda JSON
app.use(cors()); // Permite que seu frontend chame este backend

// --- A Rota Principal da API ---
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    if (!message) {
      return res.status(400).json({ error: 'Nenhuma mensagem fornecida.' });
    }

    // Inicializa o modelo (ex: Gemini 1.5 Flash)
    const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

    // Gera a resposta
    const result = await model.generateContent(message);
    const response = await result.response;
    const text = response.text();

    // Envia a resposta de volta para o frontend
    res.json({ reply: text });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Erro ao processar a mensagem.' });
  }
});

// --- Iniciar o Servidor ---
app.listen(port, () => {
  console.log(`Servidor rodando na porta ${port}`);
});