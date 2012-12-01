gramps(1)                4.0.0               gramps(1)


**NOME**
----

gramps - Programa para pesquisa geneal?gica.


**RESUMO**
------

**gramps** [**-?|--help**] [**--usage**] [**--version**] [**-l**] [**-u
|--force-unlock**] [**-O|--open=** *BANCODEDADOS* [**-f|--format=**
*FORMATO*]] [**-i|--import=** *ARQUIVO* [**-f|--format=** *FORMATO*]]
[**-i|--import=** *...*] [**-e|--export=** *ARQUIVO* [**-f|--format=**
*FORMATO*]] [**-a|--action=** *A??O*] [**-p|--options=** *OP??ES*]] [
*ARQUIVO* ] [**--version**]


**DESCRI??O**
-----------

*Gramps* ? um programa de genealogia livre e de c?digo aberto. Ele ? escrito
em Python e usa a interface GTK+/GNOME. Gramps deve parecer familiar a
qualquer pessoa que j? tenha usado outro programa de genealogia, tais como o
*Family Tree Maker (TM)*, *Personal Ancestral Files (TM)*, ou o GNU Geneweb.
Ele suporta a importa??o do formato GEDCOM, que ? amplamente usado por quase
todos os outros programas de genealogia.


OP??ES
--------

**gramps*** ARQUIVO* Quando *ARQUIVO* for indicado (sem qualquer outra op??o)
como um nome de ?rvore geneal?gica ou como pasta do banco de dados, ela ser?
aberta e iniciada uma sess?o interativa. Se ARQUIVO for um formato
compreendido pelo Gramps, ser? criada uma ?rvore geneal?gica vazia com o nome
baseado no *ARQUIVO* e os dados s?o importados para ela. As demais op??es
ser?o ignoradas. Esta forma de execu??o ? apropriada para usar o Gramps como
manipulador de dados geneal?gicos em, por exemplo, navegadores Web. Este
m?todo aceita qualquer formato de dados nativo do Gramps, conforme abaixo.


**-f,--format=*** FORMATO* Indica expressamente o formato do *ARQUIVO*,
precedente das op??es **-i** ou **-e**. Se a op??o **-f** n?o for fornecida
para um *ARQUIVO*, o formato ser? identificado de acordo com a sua extens?o
ou tipo MIME.


Os formatos dispon?veis para exporta??o s?o **gramps-xml** (se o *ARQUIVO*
terminar com **.gramps**), **gedcom** (se o *ARQUIVO* terminar com **.ged**)
ou qualquer outro formato de arquivo dispon?vel atrav?s do sistema de plugins
do Gramps.


Os formatos dispon?veis para importa??o s?o **grdb**, **gramps-xml**,
**gedcom**, **gramps-pkg** (se o *ARQUIVO* terminar com **.gpkg**), e
**geneweb** (se o *ARQUIVO* terminar com **.gw**).


Os formatos dispon?veis para exporta??o s?o **gramps-xml**, **gedcom**,
**gramps-pkg**, **wft** (se o *ARQUIVO* terminar com **.wft**), **geneweb**,
e **iso** (deve sempre ser indicado com a op??o **-f**).

**-l** Exibe uma lista com as ?rvores geneal?gicas conhecidas.

**-u,--force-unlock** Desbloqueia um banco de dados previamente bloqueado.

**-O,--open=*** BANCODEDADOS* Abre o *BANCODEDADOS*, que deve ser uma pasta
de banco de dados ou um nome de ?rvore geneal?gica existentes. Se n?o forem
indicadas op??es de a??o, importa??o ou exporta??o na linha de comando, ser?
iniciada uma sess?o interativa usando este banco de dados.

**-i,--import=*** ARQUIVO* Importa os dados do *ARQUIVO*. Se n?o for indicado
um banco de dados, o Gramps usar? um arquivo tempor?rio, que ser? exclu?do ao
sair do programa.


Quando mais de um arquivo de origem for indicado, cada um deles deve ser
precedido da op??o **-i**. Os arquivos s?o importados na ordem indicada, por
exemplo, **-i** *ARQUIVO1* **-i** *ARQUIVO2* e **-i** *ARQUIVO2* **-i**
*ARQUIVO1* poder? produzir diferentes gramps IDs no banco de dados
resultante.

**-a,--action=*** A??O* Executa a *A??O* nos dados importados. Isto ser?
executado ap?s a conclus?o de todas as importa??es. At? o momento, as a??es
dispon?veis s?o **summary** (o mesmo que Relat?rios->Exibir->Resumo),
**check** (o mesmo que Ferramentas->Processamento do banco de
dados->Verificar e reparar), **report** (gera o relat?rio), e **tool**
(executa uma ferramenta de plugin). Para o **report** e **tool** ? necess?rio
fornecer *OP??ES* (com uso da op??o **-p**).


As *OP??ES* devem satisfazer as seguintes condi??es:
N?o podem conter espa?os. Se alguns argumentos precisam incluir espa?os, a
string deve ser colocada entre aspas, ou seja, seguir a sintaxe do shell.
String de op??o ? uma lista de pares com o nome e o valor (separados por
sinal de igual). Os pares de nome e valor devem ser separados por v?rgula.


Muitas op??es s?o espec?ficas de cada relat?rio ou ferramenta. Entretanto,
algumas op??es s?o comuns.

**name=nome**
Esta op??o obrigat?ria determina qual relat?rio ou ferramenta ser? executado.
Se o *nome* fornecido n?o corresponder a um relat?rio ou ferramenta, ser?
exibida uma mensagem de erro seguida de uma lista de relat?rios e ferramentas
dispon?veis (dependendo da *A??O*).

**show=all**
Isto ir? gerar uma lista com os nomes para todas as op??es dispon?veis de um
determinado relat?rio ou ferramenta.

**show=nome_op??o**
Isto ir? exibir a descri??o da funcionalidade indicada por *nome_op??o*, bem
como quais s?o os tipos aceit?veis e os valores para esta op??o.


Use as op??es acima para descobrir tudo sobre um determinado relat?rio.

Quando mais de uma a??o de sa?da for indicada, cada uma deve ser precedida da
op??o **-a**. As a??es s?o realizadas uma a uma, na ordem indicada.

**-d,--debug=*** ARQUIVO_REGISTRO* Ativa os registros para desenvolvimento e
testes. Veja o c?digo-fonte para mais detalhes. **--version** Exibe o n?mero
da vers?o do Gramps e finaliza.


Opera??o
----------


Se o primeiro argumento da linha de comando n?o come?ar com um tra?o (isto ?,
sem uma op??o), o Gramps tentar? abrir o arquivo com o nome fornecido pelo
primeiro argumento e iniciar a sess?o interativa, ignorando o resto dos
argumentos da linha de comando.

Se for fornecida a op??o **-O**, ent?o o Gramps tentar? abrir o banco de
dados indicado e trabalhar com estes dados, de acordo com as instru??es dos
par?metros adicionais da linha de comando.

Com ou sem a op??o **-O**, pode haver m?ltiplas importa??es, exporta??es e
a??es indicadas pela linha de comando usando as op??es **-i**, **-e** e
**-a**.

A ordem das op??es **-i**, **-e** ou **-a** n?o importa. A ordem utilizada
ser? sempre esta: todas as importa??es (se existirem) -> todas as a??es (se
existirem) -> todas as exporta??es (se existirem). Mas a abertura deve estar
sempre em primeiro lugar!

Se as op??es **-O** ou **-i** n?o forem fornecidas, o Gramps ser? aberto com
a sua janela principal e iniciar? a sess?o interativa padr?o com um banco de
dados vazio, uma vez que n?o h? nada a processar.

Se as op??es **-e** ou **-a** n?o forem fornecidas, o Gramps ser? aberto com
a sua janela principal e iniciar? a sess?o interativa padr?o com um banco de
dados resultante de todas as importa??es. Este banco de dados est? localizado
no arquivo **import_db.grdb** da pasta **~/.gramps/import**.

Os erros encontrados durante a importa??o, exporta??o ou a??o, ser?o
direcionados para *stdout* (se forem exce??es tratadas pelo Gramps) ou para
*stderr* (se n?o forem tratadas). Use redirecionamentos usuais de *stdout* e
*stderr* do shell para salvar mensagens e erros em arquivos.


EXEMPLOS
--------

Abrir uma ?rvore geneal?gica existente e importar um arquivo xml para ela:
**gramps** **-O** *'Minha ?rvore geneal?gica'* **-i** *~/db3.gramps* Fazer as
mesmas altera??es da ?rvore geneal?gica do comando anterior, mas importar a
?rvore geneal?gica tempor?ria e iniciar uma sess?o interativa: **gramps**
**-i** *'Minha ?rvore geneal?gica'* **-i** *~/db3.gramps* Importar quatro
bancos de dados (cujos formatos podem ser reconhecidos pelos nomes) e
verificar a exist?ncia de erros no banco de dados resultante: **gramps**
**-i** *arquivo1.ged* **-i** *arquivo2.tgz* **-i** *~/db3.gramps* **-i**
*arquivo4.wft* **-a** *check* Indicar de forma expl?cita os formatos do
exemplo acima, atribuindo os nomes dos arquivos com as op??es **-f**
apropriadas: **gramps** **-i** *arquivo1.ged* **-f** *gedcom* **-i**
*arquivo2.tgz* **-f** *gramps-pkg* **-i** *~/db3.gramps* **-f** *gramps-xml*
**-i** *arquivo4.wft* **-f** *wft* **-a** *check* Gravar o banco de dados
resultante de todas as importa??es, indicando a op??o **-e** (use **-f** se o
nome do arquivo n?o permirtir que o gramps reconhe?a o formato
automaticamente): **gramps** **-i** *arquivo1.ged* **-i** *arquivo2.tgz*
**-e** *~/novo-pacote* **-f** *gramps-pkg* Importar tr?s bancos de dados e
iniciar a sess?o interativa do Gramps com o resultado: **gramps** **-i**
*arquivo1.ged* **-i** *arquivo2.tgz* **-i** *~/db3.gramps* Executar a
ferramenta de verifica??o a partir da linha de comando e direcionar o
resultado para stdout: **gramps** **-O** *'Minha ?rvore geneal?gica'* **-a**
*tool* **-p** **name**=*verify* Finalmente, para iniciar uma sess?o
interativa normal, digite: **gramps**


VARI?VEIS DE AMBIENTE
----------------------

O programa verifica se estas vari?veis de ambiente est?o definidas:

**LANG** - identifica o idioma a ser usado. Ex.: Para o idioma portugu?s do
Brasil, a vari?vel deve ser definida como pt_BR.UTF-8.

**GRAMPSHOME** - se definida, for?a o Gramps a usar a pasta indicada para
armazenar as configura??es e os bancos de dados do programa. Por padr?o, esta
vari?vel n?o ? definida e o Gramps assume que a pasta com todos os bancos de
dados e configura??es do perfil devem ser criadas na pasta do usu?rio
(descrita na vari?vel de ambiente HOME no Linux ou USERPROFILE no Windows
2000/XP).


CONCEITOS
---------

Suporta um sistema de plugins baseado em Python, permitindo acrescentar
importa??es e exporta??es adicionais, geradores de relat?rios, ferramentas e
filtros de exibi??o, sem modifica??o do programa principal.

Al?m da impress?o direta, ? poss?vel gerar relat?rios em diversos formatos de
arquivo, tais como *OpenOffice.org*, *AbiWord*, HTML ou LaTeX, para permitir
aos usu?rios a modifica??o de acordo com suas necessidades.


LIMITA??ES E ERROS CONHECIDOS
-------------------------------


ARQUIVOS
--------

*${PREFIX}/bin/gramps*
*${PREFIX}/share/gramps*
*${HOME}/.gramps*


AUTORES
-------

Donald Allingham *<`don@gramps-project.org`_>*
*`http://gramps.sourceforge.net`_*

Este manual foi originalmente escrito por:
Brandon L. Griffith *<`brandon@debian.org`_>*
para inclus?o na distribui??o Debian GNU/Linux.

Este manual ? atualmente mantido pelo:
Projeto Gramps *<`xxx@gramps-project.org`_>*



DOCUMENTA??O
--------------

A documenta??o para usu?rios est? dispon?vel atrav?s da op??o de ajuda padr?o
do GNOME, na forma de Manual do Gramps. O Manual tamb?m est? dispon?vel no
formato XML como **gramps-manual.xml** em *doc/gramps-manual/$LANG* nas
fontes oficiais da sua distribui??o.

A documenta??o para desenvolvedores pode ser encontrada na p?gina
*`http://developers.gramps-project.org`_*.


TRADU??O
----------

``Andr? Marcelo Alvarenga <`andrealvarenga@gmx.net`_> em 05/08/2012``

--------


Index
-----

`NOME`_ `RESUMO`_ `DESCRI??O`_ `OP??ES`_ `Opera??o`_ `EXEMPLOS`_ `VARI?VEIS
DE AMBIENTE`_ `CONCEITOS`_ `LIMITA??ES E ERROS CONHECIDOS`_ `ARQUIVOS`_
`AUTORES`_ `DOCUMENTA??O`_ `TRADU??O`_

--------

This document was created by `man2html`_, using the manual pages.
Time: 16:19:23 GMT, December 01, 2012

.. _Index: #index
.. _Return to Main Contents: /cgi-bin/man/man2html
.. _don@gramps-project.org: mailto:don@gramps-project.org
.. _http://gramps.sourceforge.net: http://gramps.sourceforge.net
.. _brandon@debian.org: mailto:brandon@debian.org
.. _xxx@gramps-project.org: mailto:xxx@gramps-project.org
.. _http://developers.gramps-project.org: http://developers.gramps-
    project.org
.. _andrealvarenga@gmx.net: mailto:andrealvarenga@gmx.net
.. _NOME: #lbAB
.. _RESUMO: #lbAC
.. _DESCRI??O: #lbAD
.. _OP??ES: #lbAE
.. _Opera??o: #lbAF
.. _EXEMPLOS: #lbAG
.. _VARI?VEIS DE AMBIENTE: #lbAH
.. _CONCEITOS: #lbAI
.. _LIMITA??ES E ERROS CONHECIDOS: #lbAJ
.. _ARQUIVOS: #lbAK
.. _AUTORES: #lbAL
.. _DOCUMENTA??O: #lbAM
.. _TRADU??O: #lbAN
