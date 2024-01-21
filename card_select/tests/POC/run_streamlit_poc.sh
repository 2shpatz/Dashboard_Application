

pip3 install streamlit

if [[! ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    export PATH=$PATH:$HOME/.local/bin
fi
streamlit run streamlit_poc.py --server.port 8050 --server.address 0.0.0.0