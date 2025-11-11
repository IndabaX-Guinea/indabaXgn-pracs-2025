# Practical 3: Recurrent Neural Networks (RNNs)

## 🎯 Learning Objectives

By the end of this practical, you will:
- Understand sequential data processing
- Build and train RNNs, LSTMs, and GRUs
- Apply RNNs to text classification and generation
- Handle variable-length sequences
- Learn about sequence-to-sequence models

## 📚 Topics Covered

1. **Sequential Data**
   - Time series
   - Text and language data
   - Sequence representation
   - Temporal dependencies

2. **Recurrent Neural Networks**
   - Vanilla RNNs
   - Hidden state
   - Backpropagation through time
   - Vanishing gradient problem

3. **Advanced RNN Architectures**
   - Long Short-Term Memory (LSTM)
   - Gated Recurrent Units (GRU)
   - Bidirectional RNNs
   - When to use which architecture

4. **Text Processing**
   - Tokenization
   - Embeddings
   - Padding and batching
   - Vocabulary building

5. **Applications**
   - Sentiment analysis
   - Text generation
   - Time series prediction
   - Sequence classification

## 🛠️ Prerequisites

- Completion of Practical 1 and 2
- Basic understanding of sequences
- Familiarity with text data

## 📝 Exercises

The notebook contains the following exercises:

1. **Exercise 3.1**: Build a simple RNN from scratch
2. **Exercise 3.2**: Implement an LSTM for sentiment analysis
3. **Exercise 3.3**: Text generation with RNNs
4. **Exercise 3.4**: Time series prediction
5. **Exercise 3.5**: Compare RNN, LSTM, and GRU

## 🚀 Getting Started

1. Open `notebook.ipynb` in Jupyter
2. Ensure you have completed previous practicals
3. Download the text dataset (instructions in notebook)
4. Follow along and complete the exercises

## 📖 Additional Resources

- [Understanding LSTM Networks](http://colah.github.io/posts/2015-08-Understanding-LSTMs/)
- [The Unreasonable Effectiveness of RNNs](http://karpathy.github.io/2015/05/21/rnn-effectiveness/)
- [PyTorch RNN Tutorial](https://pytorch.org/tutorials/intermediate/char_rnn_classification_tutorial.html)
- [Deep Learning Book - Chapter 10](http://www.deeplearningbook.org/contents/rnn.html)
- [Text Classification with RNNs](https://www.tensorflow.org/text/tutorials/text_classification_rnn)

## ⏱️ Estimated Time

3-4 hours

## 💡 Tips

- Start with small sequence lengths and vocabularies
- Gradient clipping helps prevent exploding gradients
- Visualize attention weights if implementing attention
- Experiment with different hidden sizes
- Save your trained models for text generation
