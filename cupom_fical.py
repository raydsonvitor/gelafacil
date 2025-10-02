import json
import requests

# Token e CSC
token = '1'  # Identificador do Token
csc = '5DC9D97F-C368-463A-A1A5-6FB94036523E'

'''
<NFe xmlns="http://www.portalfiscal.inf.br/nfe">
  <infNFe versao="4.00">
    <ide>
      <cUF>35</cUF>
      <cNF>12345678</cNF>
      <natOp>Venda</natOp>
      <mod>65</mod>
      <serie>1</serie>
      <nNF>1000</nNF>++++++++++
      <dhEmi>2024-10-22T10:30:00-03:00</dhEmi>
      <tpNF>1</tpNF>
      <idDest>1</idDest>
      <tpImp>4</tpImp>
      <tpEmis>1</tpEmis>
      <cMunFG>3550308</cMunFG>
      <tpAmb>2</tpAmb>
      <finNFe>1</finNFe>
      <indFinal>1</indFinal>
      <indPres>1</indPres>
    </ide>

    <emit>
      <CNPJ>12345678000195</CNPJ>
      <xNome>Loja Fictícia Ltda</xNome>
      <xFant>Loja Fictícia</xFant>
      <enderEmit>
        <xLgr>Rua Exemplo</xLgr>
        <nro>100</nro>
        <xBairro>Centro</xBairro>
        <cMun>3550308</cMun>
        <xMun>São Paulo</xMun>
        <UF>SP</UF>
        <CEP>01010000</CEP>
        <cPais>1058</cPais>
        <xPais>Brasil</xPais>
      </enderEmit>
      <IE>123456789</IE>
    </emit>

    <dest>
      <CPF>12345678909</CPF>
      <xNome>Cliente Exemplo</xNome>
      <enderDest>
        <xLgr>Rua do Cliente</xLgr>
        <nro>123</nro>
        <xBairro>Bairro Cliente</xBairro>
        <cMun>3550308</cMun>
        <xMun>São Paulo</xMun>
        <UF>SP</UF>
        <CEP>02020000</CEP>
        <cPais>1058</cPais>
        <xPais>Brasil</xPais>
      </enderDest>
    </dest>

    <det nItem="1">
      <prod>
        <cProd>001</cProd>
        <xProd>Produto Exemplo</xProd>
        <NCM>12345678</NCM>
        <CFOP>5102</CFOP>
        <uCom>UN</uCom>
        <qCom>2.0000</qCom>
        <vUnCom>10.00</vUnCom>
        <vProd>20.00</vProd>
      </prod>
      <imposto>
        <ICMS>
          <ICMS00>
            <orig>0</orig>
            <CST>00</CST>
            <modBC>3</modBC>
            <vBC>20.00</vBC>
            <pICMS>18.00</pICMS>
            <vICMS>3.60</vICMS>
          </ICMS00>
        </ICMS>
      </imposto>
    </det>

    <total>
      <ICMSTot>
        <vBC>20.00</vBC>
        <vICMS>3.60</vICMS>
        <vProd>20.00</vProd>
        <vNF>20.00</vNF>
      </ICMSTot>
    </total>

    <pag>
      <detPag>
        <tPag>01</tPag>
        <vPag>20.00</vPag>
      </detPag>
    </pag>

    <infAdic>
      <infCpl>Informações complementares aqui.</infCpl>
    </infAdic>
  </infNFe>
</NFe>
'''