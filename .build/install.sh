#!/bin/bash
set -eu
# Testar em imagem docker local
#docker run -it --rm amazonlinux:2023 /bin/bash
#yum groupinstall "Development Tools" -y
#yum install zlib zlib-devel bzip2-devel openssl-devel sqlite-devel readline-devel libffi-devel -y
#yum install git tar gcc make -y
#git clone https://gitlab.com/SrMouraSilva/canta-igreja-api
#cd canta-igreja-api

echo "🚀 [install.sh] Iniciando script de instalação..."
echo "🔎 [install.sh] Verificando versão do Python:" 
python3 --version


#if [ -n "${CI}" ]; then
#  echo "🤖 [install.sh] Ambiente CI detectado, instalando sqlite-devel"
#  yum -y install sqlite-devel
#else
#  echo "🐞 [install.sh] Ambiente CI não detectado; pulando instalação do sqlite-devel."
#fi

#echo "📦 [install.sh] Instalando dependências do projeto"
#pip3 install -r requirements.txt
#echo "📦 [install.sh] Instalando dependências para a geração dos arquivos .json"
#pip3 install -r gerador_banco/requirements.txt

#echo "🔁 [install.sh] Verificando versão do Python novamente:" 
#python3 --version

mkdir -p api/public/biblioteca/obras
mkdir -p api/public/musicas

echo "🗂️  [install.sh] Criadas pastas públicas (api/public/...)"
echo "⚙️  [install.sh] Criando arquivos .json a serem disponibilizados pela API"
python3 -m pip install -r requirements.txt
python3 build_api.py
echo "✅ [install.sh] build_api.py finalizado."

if [ -n "${DEPLOY_LANDING_PAGE_URL:-}" ]; then
  echo "📬 [install.sh] Requisitando um novo deploy do portal de produção"
  curl -X POST $DEPLOY_LANDING_PAGE_URL
fi

if [ -n "${DEPLOY_LANDING_PAGE_URL_PREVIEW:-}" ]; then
  echo "📬 [install.sh] Requisitando um novo deploy do portal de preview"
  curl -X POST $DEPLOY_LANDING_PAGE_URL_PREVIEW
fi

echo "🎉 [install.sh] Script concluído com sucesso."
