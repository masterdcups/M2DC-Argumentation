<?xml version="1.0" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Output to text (csv) -->
  <xsl:output method="text"/>

  <!-- Root -->
  <xsl:template match="/">
    <xsl:apply-templates select="//h1" />
    <xsl:apply-templates mode="descr" select="//div[@id='content']//div[count(preceding-sibling::h2)=1]" />
    <xsl:apply-templates mode="pro" select="//div[count(preceding-sibling::h2)=3]" />
    <xsl:apply-templates mode="con" select="//div[count(preceding-sibling::h2)=4]" />
  </xsl:template>

  <!-- Name -->
  <xsl:template match="h1">
    <xsl:text>#name: </xsl:text>
    <xsl:value-of select="." />
    <xsl:text>&#xa;</xsl:text> <!-- newline -->
  </xsl:template>

  <!-- Description -->
  <xsl:template mode="descr" match="div">
    <xsl:text>#description: </xsl:text>
    <xsl:value-of select="." />
    <xsl:text>&#xa;</xsl:text> <!-- newline -->
  </xsl:template>

  <!-- Arguments (pros) -->
  <xsl:template mode="pro" match="div">
    <xsl:variable name="url" select=".//a[1]/@href" />
    <xsl:if test="not(contains($url, ':'))">
      <xsl:value-of select="$url" />
    </xsl:if>
    <xsl:text>;</xsl:text>
    <xsl:value-of select="./h3" />
    <xsl:text>;1</xsl:text>
    <xsl:text>&#xa;</xsl:text> <!-- newline -->
  </xsl:template>
  
  <!-- Arguments (cons) -->
  <xsl:template mode="con" match="div">
    <xsl:variable name="url" select=".//a[1]/@href" />
    <xsl:if test="not(contains($url, ':'))">
      <xsl:value-of select="$url" />
    </xsl:if>
    <xsl:text>;</xsl:text> <!-- newline -->
    <xsl:value-of select="./h3" />
    <xsl:text>;-1</xsl:text>
    <xsl:text>&#xa;</xsl:text> <!-- newline -->
  </xsl:template>

</xsl:stylesheet>
