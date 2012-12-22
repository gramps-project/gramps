Portuguese (Brazil)
===================

gramps(1)                4.0.0               gramps(1)


**NOME**

        gramps - Programa para pesquisa genealógica.


**RESUMO**

        gramps [-?|--help] [--usage] [--version] [-l] [-u|--force-unlock]
        [-O|--open= BANCODEDADOS [-f|--format= FORMATO]] [-i|--import= ARQUIVO 
        [-f|--format= FORMATO]] [-i|--import= ...] [-e|--export= ARQUIVO 
        [-f|--format= FORMATO]] [-a|--action= AÇÃO] [-p|--options= OPÇÕES]] 
        [ ARQUIVO ] [--version]


**DESCRIÇÃO**

        Gramps é um programa de genealogia livre e de código aberto. 
        Ele é escrito em Python e usa a interface GTK+/GNOME. 
        Gramps deve parecer familiar a qualquer pessoa que já tenha usado 
        outro programa de genealogia, tais como o Family Tree Maker (TM), 
        Personal Ancestral Files (TM), ou o GNU Geneweb. Ele suporta a 
        importação do formato GEDCOM, que é amplamente usado por quase 
        todos os outros programas de genealogia.


**OPÇÕES**

       **gramps** *ARQUIVO*
        Quando *ARQUIVO* for indicado (sem qualquer outra opção) como um 
        nome de árvore genealógica ou como pasta do banco de dados, 
        ela será aberta e iniciada uma sessão interativa. Se *ARQUIVO* for 
        um formato compreendido pelo Gramps, será criada uma árvore 
        genealógica vazia com o nome baseado no ARQUIVO e os dados são 
        importados para ela. As demais opções serão ignoradas. Esta 
        forma de execução é apropriada para usar o Gramps como manipulador 
        de dados genealógicos em, por exemplo, navegadores Web. Este método 
        aceita qualquer formato de dados nativo do Gramps, conforme abaixo. 


       **-f** , **--format=** *FORMATO*
        Indica expressamente o formato do *ARQUIVO*, precedente das opções 
        -i ou -e. Se a opção -f não for fornecida para um ARQUIVO, o 
        formato será identificado de acordo com a sua extensão ou tipo MIME. 

        Os formatos disponíveis para exportação são gramps-xml (se o ARQUIVO 
        terminar com .gramps), gedcom (se o ARQUIVO terminar com .ged) ou 
        qualquer outro formato de arquivo disponível através do sistema de 
        plugins do Gramps. 


        Os formatos disponíveis para importação são grdb, gramps-xml, gedcom, 
        gramps-pkg (se o ARQUIVO terminar com .gpkg), e geneweb 
        (se o ARQUIVO terminar com .gw). 


        Os formatos disponíveis para exportação são gramps-xml, gedcom, 
        gramps-pkg, wft (se o ARQUIVO terminar com .wft), geneweb.

       **-l**
        Exibe uma lista com as árvores genealógicas conhecidas.


       **-u** , **--force-unlock**
        Desbloqueia um banco de dados previamente bloqueado.


       **-O** , **--open=** *BANCODEDADOS*
        Abre o *BANCODEDADOS* , que deve ser uma pasta de banco de dados 
        ou um nome de árvore genealógica existentes. Se não forem indicadas 
        opções de ação, importação ou exportação na linha de comando, 
        será iniciada uma sessão interativa usando este banco de dados.


       **-i** , **--import=** *ARQUIVO*
        Importa os dados do ARQUIVO. Se não for indicado um banco de dados, 
        o Gramps usará um arquivo temporário, que será excluído ao sair 
        do programa. 


        Quando mais de um arquivo de origem for indicado, cada um deles 
        deve ser precedido da opção -i. Os arquivos são importados na ordem 
        indicada, por exemplo, -i ARQUIVO1 -i ARQUIVO2 e -i ARQUIVO2 -i 
        ARQUIVO1 poderá produzir diferentes gramps IDs no banco de dados 
        resultante.


       **-a** , **--action=** *AÇÃO*
        Executa a *AÇÃO* nos dados importados. Isto será executado após a 
        conclusão de todas as importações. Até o momento, as ações 
        disponíveis são summary (o mesmo que Relatórios->Exibir->Resumo), 
        check (o mesmo que Ferramentas->Processamento do banco de dados->
        Verificar e reparar), report (gera o relatório), e tool (executa 
        uma ferramenta de plugin). Para o report e tool é necessário 
        fornecer OPÇÕES (com uso da opção -p). 


        As OPÇÕES devem satisfazer as seguintes condições: 
        Não podem conter espaços. Se alguns argumentos precisam incluir 
        espaços, a string deve ser colocada entre aspas, ou seja, seguir 
        a sintaxe do shell. String de opção é uma lista de pares com o 
        nome e o valor (separados por sinal de igual). Os pares de nome 
        e valor devem ser separados por vírgula. 


        Muitas opções são específicas de cada relatório ou ferramenta. 
        Entretanto, algumas opções são comuns.

        **name=nome** 
        Esta opção obrigatória determina qual relatório ou ferramenta 
        será executado. Se o nome fornecido não corresponder a um 
        relatório ou ferramenta, será exibida uma mensagem de erro 
        seguida de uma lista de relatórios e ferramentas disponíveis 
        dependendo da AÇÃO).

        **show=all**
        Isto irá gerar uma lista com os nomes para todas as opções 
        disponíveis de um determinado relatório ou ferramenta.

        **show=nome_opção**
        Isto irá exibir a descrição da funcionalidade indicada por nome_opção, 
        bem como quais são os tipos aceitáveis e os valores para esta opção.


        Use as opções acima para descobrir tudo sobre um determinado relatório.

        Quando mais de uma ação de saída for indicada, cada uma deve ser 
        precedida da opção -a. As ações são realizadas uma a uma, na ordem 
        indicada.

       **-d** , **--debug=** *ARQUIVO_REGISTRO*
        Ativa os registros para desenvolvimento e testes. Veja o código-fonte 
        para mais detalhes.
        
       **--version**
        Exibe o número da versão do Gramps e finaliza.
 
**Operação**
        Se o primeiro argumento da linha de comando não começar com um 
        traço (isto é, sem uma opção), o Gramps tentará abrir o arquivo 
        com o nome fornecido pelo primeiro argumento e iniciar a sessão 
        interativa, ignorando o resto dos argumentos da linha de comando.


        Se for fornecida a opção -O, então o Gramps tentará abrir o banco 
        de dados indicado e trabalhar com estes dados, de acordo com as 
        instruções dos parâmetros adicionais da linha de comando.


        Com ou sem a opção -O, pode haver múltiplas importações, exportações 
        e ações indicadas pela linha de comando usando as opções -i, -e e -a.


        A ordem das opções -i, -e ou -a não importa. A ordem utilizada 
        será sempre esta: todas as importações (se existirem) -> todas 
        as ações (se existirem) -> todas as exportações (se existirem). 
        Mas a abertura deve estar sempre em primeiro lugar!


        Se as opções -O ou -i não forem fornecidas, o Gramps será aberto 
        com a sua janela principal e iniciará a sessão interativa padrão 
        com um banco de dados vazio, uma vez que não há nada a processar.


        Se as opções -e ou -a não forem fornecidas, o Gramps será aberto 
        com a sua janela principal e iniciará a sessão interativa padrão 
        com um banco de dados resultante de todas as importações. Este 
        banco de dados está localizado no arquivo import_db.grdb da 
        pasta ~/.gramps/import.


        Os erros encontrados durante a importação, exportação ou ação, 
        serão direcionados para stdout (se forem exceções tratadas pelo 
        Gramps) ou para stderr (se não forem tratadas). Use redirecionamentos 
        usuais de stdout e stderr do shell para salvar mensagens e erros 
        em arquivos.



**EXEMPLOS**

        Abrir uma árvore genealógica existente e importar um arquivo xml para 
        ela:
        
           gramps -O 'Minha árvore genealógica' -i ~/db3.gramps

        Fazer as mesmas alterações da árvore genealógica do comando anterior, 
        mas importar a árvore genealógica temporária e iniciar uma sessão 
        interativa:
        
           gramps -i 'Minha árvore genealógica' -i ~/db3.gramps

        Importar quatro bancos de dados (cujos formatos podem ser 
        reconhecidos pelos nomes) e verificar a existência de erros no 
        banco de dados resultante:
        
           gramps -i arquivo1.ged -i arquivo2.tgz -i ~/db3.gramps -i 
           arquivo4.wft -a check

        Indicar de forma explícita os formatos do exemplo acima, atribuindo 
        os nomes dos arquivos com as opções -f apropriadas:
        
           gramps -i arquivo1.ged -f gedcom -i arquivo2.tgz -f gramps-pkg 
           -i ~/db3.gramps -f gramps-xml -i arquivo4.wft -f wft -a check

        Gravar o banco de dados resultante de todas as importações, 
        indicando a opção -e (use -f se o nome do arquivo não permirtir 
        que o gramps reconheça o formato automaticamente):
        
           gramps -i arquivo1.ged -i arquivo2.tgz -e ~/novo-pacote -f gramps-pkg

        Importar três bancos de dados e iniciar a sessão interativa do 
        Gramps com o resultado:
        
           gramps -i arquivo1.ged -i arquivo2.tgz -i ~/db3.gramps

        Executar a ferramenta de verificação a partir da linha de 
        comando e direcionar o resultado para stdout:
        
           gramps -O 'Minha árvore genealógica' -a tool -p name=verify

        Finalmente, para iniciar uma sessão interativa normal, digite:
        
           gramps
 
**VARIÁVEIS DE AMBIENTE**

        O programa verifica se estas variáveis de ambiente estão definidas:
        **LANG** - identifica o idioma a ser usado. Ex.: Para o idioma português do Brasil, a variável deve ser definida como pt_BR.UTF-8.

        **GRAMPSHOME** - se definida, força o Gramps a usar a pasta indicada para armazenar as configurações e os bancos de dados do programa. Por padrão, esta variável não é definida e o Gramps assume que a pasta com todos os bancos de dados e configurações do perfil devem ser criadas na pasta do usuário (descrita na variável de ambiente HOME no Linux ou USERPROFILE no Windows 2000/XP).



**CONCEITOS**

        Suporta um sistema de plugins baseado em Python, permitindo acrescentar 
        importações e exportações adicionais, geradores de relatórios, 
        ferramentas e filtros de exibição, sem modificação do programa principal.

        Além da impressão direta, é possível gerar relatórios em diversos 
        formatos de arquivo, tais como OpenOffice.org, AbiWord, HTML ou 
        LaTeX, para permitir aos usuários a modificação de acordo com 
        suas necessidades.



**LIMITAÇÕES E ERROS CONHECIDOS**

*ARQUIVOS**

       *${PREFIX}/bin/gramps*
       
       *${PREFIX}/lib/python/dist-packages/gramps/*
       
       *${PREFIX}/share/*
       
       *${HOME}/.gramps*


*AUTORES*

       Donald Allingham <don@gramps-project.org> 
       http://gramps.sourceforge.net
       Este manual foi originalmente escrito por: 
       Brandon L. Griffith <brandon@debian.org> 
       para inclusão na distribuição Debian GNU/Linux.

       Este manual é atualmente mantido pelo: 
       Projeto Gramps <xxx@gramps-project.org> 
 

**DOCUMENTAÇÃO**

        A documentação para usuários está disponível através da 
        opção de ajuda.

        A documentação para desenvolvedores pode ser encontrada na 
        página http://developers.gramps-project.org.



**TRADUÇÃO**

André Marcelo Alvarenga <andrealvarenga@gmx.net> em 05/08/2012

January 2013                 4.0.0               gramps(1)

