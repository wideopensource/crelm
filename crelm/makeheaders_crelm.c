#include <stdio.h>

// todo foss: tie this in with externla DEBUG macro
// #define DEBUG (PARSER | DECL_DUMP | TOKENIZER)

#define TEST 2 // foss: semi-hack to disable main() in makeheaders.c

// foss: unmodified from source: https://www.hwaci.com/sw/mkhdr/
#include "makeheaders.c"

// foss: note that this code is MIT-licensed but makeheaders.c is under
// the (seemingly compatible) 2-clause BSD license.

// foss: WARNING: makeheaders keeps a lot of global state which makes
// it awkward to use in a library. Make sure the state is reset between runs.

static int build_declarations(char *header, FILE *log_file) {
  GenState sState;
  String outStr;
  IdentTable includeTable;
  Decl *pDecl;

  sState.pStr = &outStr;
  StringInit(&outStr);

  sState.pTable = &includeTable;
  memset(&includeTable, 0, sizeof(includeTable));
  sState.zIf = 0;
  sState.nErr = 0;
  sState.zFilename = "(all)";
  sState.flags = 0;

  ResetDeclFlags(0);

  for (pDecl = pDeclFirst; pDecl; pDecl = pDecl->pNext) {
    DeclareObject(pDecl, &sState, 1);
  }

  ChangeIfContext(0, &sState);
  strcpy(header, StringGet(&outStr));

#ifdef DEBUG
  fprintf(log_file, "emitting decl: '%s'\n", header);
#endif

  IdentTableReset(&includeTable);
  StringReset(&outStr);
  return 0;
}

int make_header(char const *source, char *header) {
  Token *pList;
  FILE *log_file = stdout;
  IdentTable idTable;
  int rv = 0;

#ifdef DEBUG
  debugMask = DEBUG;

  fprintf(log_file, "%s -> %s\n", source, header);
#endif

  memset(&idTable, 0, sizeof(IdentTable));
  pDeclFirst = 0;
  pDeclLast = 0;

#ifdef DEBUG
  printf("%s", source);
#endif

  pList = TokenizeFile(source, &idTable);

  if (!pList) {
    fprintf(log_file, "Errors while processing source\n");
    return 1;
  }

  rv = ParseFile(pList, 0);
  if (!rv) {
    rv = build_declarations(header, log_file);
  }

  fflush(log_file);
  FreeTokenList(pList);

  return rv;
}
