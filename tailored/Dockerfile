FROM texlive/texlive:latest-small

# Install missing LaTeX packages via tlmgr
RUN tlmgr install enumitem titlesec hyperref lm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-yaml \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /resume

ENTRYPOINT ["lualatex"]
