# Outer script for building PL/SQL for SELECT queries
outer_script_select = """
DECLARE
    v_cursor   NUMBER;
    v_sql_stmt VARCHAR2(32000);
    v_output   VARCHAR2(32000); 
    v_ind      NUMBER;
    v_start     NUMBER := :start;
    v_end       NUMBER := :end;
BEGIN
    v_sql_stmt := 'REPLACE_ME';
    v_cursor := dbms_sql.open_cursor@replace_link;
    dbms_sql.parse@replace_link(v_cursor, v_sql_stmt, dbms_sql.native);
    dbms_sql.bind_variable@replace_link(v_cursor, ':output', v_output, 32000);
    dbms_sql.bind_variable@replace_link(v_cursor, ':start', v_start);
    dbms_sql.bind_variable@replace_link(v_cursor, ':end', v_end);
    v_ind := dbms_sql.execute@replace_link(v_cursor);
    dbms_sql.variable_value@replace_link(v_cursor, ':output', v_output);
    dbms_sql.close_cursor@replace_link(v_cursor);
    :output := v_output;
END;
"""

# Outer script for building PL/SQL for other queries (INSERT, DELETE, UPDATE, etc.)
outer_script_other = """
DECLARE
    v_cursor   NUMBER;
    v_sql_stmt VARCHAR2(32000);
    v_output   VARCHAR2(32000); 
    v_ind      NUMBER;
BEGIN
    v_sql_stmt := 'REPLACE_ME';
    v_cursor := dbms_sql.open_cursor@replace_link;
    dbms_sql.parse@replace_link(v_cursor, v_sql_stmt, dbms_sql.native);
    dbms_sql.bind_variable@replace_link(v_cursor, ':output', v_output, 32000);
    v_ind := dbms_sql.execute@replace_link(v_cursor);
    dbms_sql.variable_value@replace_link(v_cursor, ':output', v_output);
    dbms_sql.close_cursor@replace_link(v_cursor);
    :output := v_output;
END;
"""

# Inner script for building PL/SQL for SELECT queries
inner_script_select = """
DECLARE
    PRAGMA AUTONOMOUS_TRANSACTION;
    v_cursor    NUMBER;
    v_column_count NUMBER;
    v_desc_tab     DBMS_SQL.DESC_TAB;
    v_col_num      NUMBER;
    v_varchar_val VARCHAR2(32000);
    v_output_str   VARCHAR2(32000);
    v_ind      NUMBER;
    v_start     NUMBER := :start;
    v_end       NUMBER := :end;
BEGIN
    v_cursor := DBMS_SQL.OPEN_CURSOR;
    DBMS_SQL.PARSE(v_cursor, 'SELECT * FROM (SELECT a.*, ROWNUM rnum FROM (REPLACE_ME) a WHERE ROWNUM <= ' || v_end || ') WHERE rnum >= ' || v_start, DBMS_SQL.NATIVE);
    DBMS_SQL.DESCRIBE_COLUMNS(v_cursor, v_column_count, v_desc_tab);
    
    FOR i IN 1 .. v_column_count LOOP
        DBMS_SQL.DEFINE_COLUMN(v_cursor, i, v_varchar_val, 32000);
    END LOOP;
    
    v_output_str := CHR(10) || 'RESULTS:' || CHR(10);
    v_ind := DBMS_SQL.EXECUTE(v_cursor);

LOOP
    IF DBMS_SQL.FETCH_ROWS(v_cursor) = 0 THEN
        EXIT;
    END IF;
    
    v_output_str := v_output_str || 'ROW: ' || CHR(10);
    
    FOR i IN 1 .. v_column_count LOOP
        DBMS_SQL.COLUMN_VALUE(v_cursor, i, v_varchar_val);
        v_output_str := v_output_str || v_desc_tab(i).col_name || ' = ' || v_varchar_val || CHR(10);
    END LOOP;
END LOOP;

DBMS_SQL.CLOSE_CURSOR(v_cursor);
:output := v_output_str;
END;
"""

# Inner script for building PL/SQL for other queries (INSERT, DELETE, UPDATE, etc.)
inner_script_other_ddl = """
DECLARE
    PRAGMA AUTONOMOUS_TRANSACTION;
    v_cursor   NUMBER;
    v_sql_stmt VARCHAR2(32000);
    v_sql_stmtt VARCHAR2(32000);
    v_output   VARCHAR2(32000);
    v_ind      NUMBER;
BEGIN
    v_sql_stmt := 'REPLACE_ME';
    v_cursor := dbms_sql.open_cursor;
    dbms_sql.parse(v_cursor, v_sql_stmt, dbms_sql.native);
    v_ind := dbms_sql.execute(v_cursor);
    dbms_sql.close_cursor(v_cursor);
    v_output := 'Command completed successfuly!';
    :output := v_output;
END;
"""

inner_script_other = """
DECLARE
    v_cursor   NUMBER;
    v_sql_stmt VARCHAR2(32000);
    v_sql_stmtt VARCHAR2(32000);
    v_output   VARCHAR2(32000);
    v_ind      NUMBER;
BEGIN
    v_sql_stmt := 'REPLACE_ME';
    v_cursor := dbms_sql.open_cursor;
    dbms_sql.parse(v_cursor, v_sql_stmt, dbms_sql.native);
    v_ind := dbms_sql.execute(v_cursor);
    dbms_sql.close_cursor(v_cursor);
    v_output := 'Command completed successfuly!';
    :output := v_output;
END;
"""
